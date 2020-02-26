
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string


class Command(BaseCommand):
    """
    Check for abandoned payments for event registration.
    Then email users if meet the criteria.
    
    Abandoned payments:
        Non-paid registrations for the events that Payment is required
        and Credit Card is the only payment option.

    Usage: ./manage.py check_abandoned_payments --verbosity=2
    Example: ./manage.py check_abandoned_payments --event_id=1 --verbosity=2
    """
    def add_arguments(self, parser):
        parser.add_argument('--event_id',
            dest='event_id',
            default=None,
            help='The id of the event to be processed')
    
    def email_notice(self, event, registration, verbosity=0, **kwargs):
        from tendenci.apps.notifications import models as notification
        from tendenci.apps.base.utils import validate_email
        registrant = registration.registrant
 
        if registrant and registrant.email and validate_email(registrant.email):
            recipient = registrant.email
                        
            if recipient:
                if verbosity == 2:
                    print('Sending notice email to {}'.format(recipient))
                    
                context = {'event': event,
                   'invoice': registration.invoice,
                   'reg8n': registration,
                   'registrant': registrant.user,
                   }
                context.update(kwargs)
                notification.send_emails([recipient], 'event_email_abandoned',
                                         context)
                return True

    def send_admin_confirmation(self, event, reg8n_list, verbosity=0, **kwargs):
        from tendenci.apps.notifications import models as notification
        from tendenci.apps.site_settings.utils import get_setting
        admin_emails = get_setting('module', 'events',
                                       'admin_emails').strip()
        if admin_emails:
            admin_emails = admin_emails.split(',')

        if admin_emails:
            if verbosity == 2:
                print('Sending confirmation to {}'.format(', '.join(admin_emails)))
                
            context = {'event': event,
                       'reg8n_list': reg8n_list,}
            context.update(kwargs)
            notification.send_emails(admin_emails, 'event_email_abandoned_recap',
                                     context)

    def handle(self, *args, **options):
        from tendenci.apps.events.models import Event, Registration, Organizer
        from tendenci.apps.site_settings.utils import get_setting

        verbosity = options['verbosity']
        event_id = options['event_id']
        
        if not get_setting('module', 'events', 'enable_notice_abandoned'):
            if verbosity == 2:
                print('Notification to registrants who abandoned payments .. Not enabled')
            return
        
        check_days = get_setting('module', 'events', 'days_notice_abandoned')
        days_list = []
        for day in check_days.split(','):
            try:
                days_list.append(int(day.strip()))
            except:
                continue
        if not days_list:
            if verbosity >=2: 
                print('Notification to registrants who abandoned payments .. Not specified')
            return
        
        kwargs = {'site_url': get_setting('site', 'global', 'siteurl'),
                  'site_name': get_setting('site', 'global', 'sitedisplayname')}
        
        now = datetime.now()
        today_tuple = (datetime(now.year, now.month, now.day, 0, 0, 0),
                       datetime(now.year, now.month, now.day, 23, 59, 59))

        # get a list of upcoming events that are specified to send reminders.
        events = Event.objects.filter(end_dt__gt=now,
                                registration_configuration__enabled=True,
                                registration_configuration__payment_required=True,
                                status=True,
                                status_detail='active')
        if event_id:
            events = events.filter(id=event_id)
        
        if events:
            for event in events:
                reg8n_list = []
                if event.registration_configuration.payment_method.filter(is_online=False).exists():
                    # skip if there is any non-online payment method
                    continue
                
                [organizer] = Organizer.objects.filter(event=event)[:1] or [None]
                event.organizer = organizer
                
                
                if organizer:
                    if organizer.name:
                        kwargs.update({'sender_display': organizer.namel})
                    if organizer.user and organizer.user.email:
                            kwargs.update({'reply_to': organizer.user.email})
                
                registrations = Registration.objects.filter(event=event,
                                                canceled=False,
                                                invoice__balance__gt=0)
                
                for registration in registrations:
                    create_dt = registration.create_dt
                    for day in days_list:
                        check_dt = create_dt + timedelta(days=day)
                        if today_tuple[0] <= check_dt and check_dt <= today_tuple[1]:
                            # send notice
                            sent = self.email_notice(event, registration, verbosity=verbosity, **kwargs)
                            
                            if sent:
                                reg8n_list.append(registration)

                if 'sender_display' in kwargs:
                    kwargs.pop('sender_display')
                if 'reply_to' in kwargs:
                    kwargs.pop('reply_to') 

                if reg8n_list:
                    # email event admin
                    self.send_admin_confirmation(event, reg8n_list, verbosity=verbosity, **kwargs)
