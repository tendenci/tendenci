
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string


class Command(BaseCommand):
    """
    Send email reminders to the event registrants requesting reminders.

    Usage: ./manage.py send_event_reminders --verbosity=2
    """
    

    

    def handle(self, *args, **options):
        from tendenci.apps.events.models import Event, Registrant, Organizer
        from tendenci.apps.emails.models import Email
        from tendenci.apps.site_settings.utils import get_setting
        from tendenci.apps.base.utils import convert_absolute_urls
        from tendenci.apps.events.utils import (render_event_email,
                                  get_default_reminder_template,
                                  replace_qr_code)
        
        
        def get_reminder_conf_body(event):
            template_name = 'events/reminder_conf_email.html'
    
            return render_to_string(template_name=template_name,
                           context={'event': event,
                            'site_url': get_setting('site', 'global',
                                                    'siteurl'),
                            'site_display_name': get_setting(
                                                     'site',
                                                     'global',
                                                     'sitedisplayname')
                            })

        def send_organizer_confirmation(event):    
            email = Email()
            if event.organizer_first and event.organizer_first.user \
                and event.organizer_first.user.email:
                email.recipient = event.organizer_first.user.email
            else:
                email.recipient = get_setting('module', 'events', 'admin_emails')
                if not email.recipient:
                    email.recipient = get_setting('site', 'global',
                                                  'sitecontactemail')
    
            email.subject = '%s Event Reminders Distributed for: %s' % (
                                    get_setting('site', 'global',
                                                'sitedisplayname'),
                                    event.title
                                    )
            email.body = get_reminder_conf_body(event)
    
            email.send()

        def send_reminders(event, registrants, email_rendered=True, verbosity=0):
            email = event.email
    
            count = 0
            for registrant in registrants:
                if registrant.email:
                    if verbosity == 2:
                        print('Sending reminder email to %s %s' % (
                                    registrant.first_name,
                                    registrant.last_name))
                    email.recipient = registrant.email
                    if not email_rendered:
                        original_body = email.body
                        if email.body.find('{{ qr_code }}') != -1:
                            email.body = replace_qr_code(email.body)
                        email = render_event_email(event, email, registrants=[registrant])
                        # replace the relative links with absolute urls
                        # in the email body and subject
                        email.body = convert_absolute_urls(email.body, site_url)
                        #print(email.body)
                        email.send()
                        # assign back the original body
                        email.body = original_body
                    else:
                        email.send()
                    count += 1
    
            if count > 0:
                # notify event organizer that reminders have been
                # distributed to all registrants requesting reminders.
                send_organizer_confirmation(event)

        verbosity = options['verbosity']
        site_url = get_setting('site', 'global', 'siteurl')
        now = datetime.now()
        today_tuple = (datetime(now.year, now.month, now.day, 0, 0, 0),
                       datetime(now.year, now.month, now.day, 23, 59, 59))

        # get a list of upcoming events that are specified to send reminders.
        events = Event.objects.filter(start_dt__gt=now,
                                registration_configuration__enabled=True,
                                registration_configuration__send_reminder=True,
                                status=True,
                                status_detail='active')
        events_list = []
        if events:
            for event in events:
                reg_conf = event.registration_configuration
                reminder_days = reg_conf.reminder_days
                if not reminder_days:
                    reminder_days = '1'
                days_list = reminder_days.split(',')

                for day in days_list:
                    try:
                        day = int(day)
                    except:
                        continue

                    start_dt = event.start_dt - timedelta(days=day)

                    if today_tuple[0] <= start_dt and start_dt <= today_tuple[1]:
                        events_list.append(event)

            for event in events_list:
                registrants = Registrant.objects.filter( # reminder=True,
                                registration__event=event,
                                cancel_dt=None
                                )

                reg_conf = event.registration_configuration
                organizer = event.organizer_set.all().first()
                event.organizer_first = organizer

                email = reg_conf.email
                if not email:
                    email = Email()

                if organizer:
                    if not email.sender_display:
                        if organizer.name:
                            email.sender_display = organizer.name
    
                    if not email.reply_to:
                        if organizer.user and organizer.user.email:
                            email.reply_to = organizer.user.email

                if not email.subject:
                    email.subject = 'Reminder: %s' % event.title
                else:
                    email.subject = 'Reminder: %s' % email.subject

                if not email.body:
                    email.body = get_default_reminder_template(event)

                if email.body.find('{{ qr_code }}') == -1:
                    email = render_event_email(event, email)
                    # replace the relative links with absolute urls
                    # in the email body and subject
                    email.body = convert_absolute_urls(email.body, site_url)
                    email_rendered = True
                else:
                    # will need to render individually because each registrant's qr code is different
                    email_rendered = False

                event.email = email
                send_reminders(event, registrants, email_rendered=email_rendered, verbosity=verbosity)
