from datetime import datetime, timedelta
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """
    Send email to creator when directory is available for renewal.
    """
    def handle(self, *args, **options):
        from django.utils import timezone
        from tendenci.apps.base.utils import send_email_notification
        from tendenci.apps.site_settings.utils import get_setting
        from tendenci.apps.directories.models import Directory

        # Query all events that are not yet marked for checking
        directories = Directory.objects.filter(renewal_notice_sent=False)

        days = get_setting('module', 'directories', 'renewaldays')
        days = int(days)

        for directory in directories:
            if timezone.now() + timedelta(days) > directory.expiration_dt:
                email_recipient = directory.creator.email
                print('Sending email to {} for directory {}.'.format(email_recipient, directory))
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
                print('Directory {} not eligible for renewal right now.'.format(directory))
