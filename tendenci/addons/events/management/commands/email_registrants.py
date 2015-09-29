from optparse import make_option
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    """
    Email registrants.

    Usage: ./manage.py email_registrants --event=<event_id>
                                         --email=<email_id>
                                         --user=<user_id>
                                         --payment_status=all
                                         --verbosity=2
    """
    option_list = BaseCommand.option_list + (  
        make_option(
            '--event',
            action='store',
            dest='event',
            default=0,
            help='Event ID'),
        make_option(
            '--email',
            action='store',
            dest='email',
            default=0,
            help='Email ID'),
        make_option(
            '--user',
            action='store',
            dest='user',
            default='1',
            help='Request user'),
        make_option(
            '--payment_status',
            action='store',
            dest='payment_status',
            default='all',
            help='Payment status - paid, not-paid or all'),
    )

    def handle(self, *args, **options):
        from tendenci.addons.events.models import Event
        from tendenci.addons.events.utils import email_registrants
        from tendenci.core.emails.models import Email
        from tendenci.core.site_settings.utils import get_setting
        from tendenci.core.event_logs.models import EventLog

        event_id = options['event']
        email_id = options['email']
        user_id = options['user']
        payment_status = options['payment_status']
        [event] = Event.objects.filter(id=event_id)[:1] or [None]
        [email] = Email.objects.filter(id=email_id)[:1] or [None]

        if event and email:
            kwargs = {'payment_status': payment_status}
            email_registrants(event, email, **kwargs)
            
            [user] = User.objects.filter(id=user_id)[:1] or [None]
            if user:
                kwargs['summary'] = '<font face=""Arial"" color=""#000000"">'
                kwargs['summary'] += 'Emails sent as a result of Calendar Event Notification</font><br><br>'
                kwargs['summary'] += '<font face=""Arial"" color=""#000000"">'
                kwargs['summary'] += '<br><br>Email Sent Appears Below in Raw Format'
                kwargs['summary'] += '</font><br><br>'
                kwargs['summary'] += email.body
    
                # send summary
                summary_email = Email()
                summary_email.subject = 'SUMMARY: %s' % email.subject
                summary_email.body = kwargs['summary']
                summary_email.recipient = user.email
                summary_email.send()
    
                # send another copy to the site webmaster
                summary_email.recipient = get_setting('site', 'global', 'sitewebmasteremail')
                if summary_email.recipient:
                    summary_email.subject = 'WEBMASTER SUMMARY: %s' % email.subject
                    summary_email.body = '<h2>Site Webmaster Notification of Calendar Event Send</h2>%s' % email.body
                    summary_email.send()
    
                EventLog.objects.log(instance=summary_email)
        
        