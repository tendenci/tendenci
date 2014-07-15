from datetime import datetime, timedelta
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """
    Send email to creator when directory is available for renewal.
    """
    def handle(self, *args, **options):
        from tendenci.core.base.utils import send_email_notification
        from tendenci.core.site_settings.utils import get_setting
        from tendenci.addons.directories.models import Directory

        # Query all events that are not yet marked for checking
        directories = Directory.objects.filter(renewal_notice_sent=False)

        days = get_setting('module', 'directories', 'renewaldays')
        days = int(days)

        for directory in directories:
            if datetime.now() + timedelta(days) > directory.expiration_dt:
                email_recipient = directory.creator.email
                print 'Sending email to %s for directory %s.' % (email_recipient, directory, )
                send_email_notification(
                    'directory_renewal_eligible',
                    email_recipient,
                    {
                    'directory': directory,
                    }
                )

                directory.renewal_notice_sent = True
                directory.save()
            else:
                print 'Directory %s not eligible for renewal right now.' % (directory, )