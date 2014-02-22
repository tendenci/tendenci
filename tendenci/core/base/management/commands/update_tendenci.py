import os, subprocess
from optparse import make_option

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.core.management import call_command, CommandError


class Command(BaseCommand):
    """
    Update tendenci via pip and restarts the server
    """

    option_list = BaseCommand.option_list + (
        make_option(
            '--user',
            action='store',
            dest='user',
            default='',
            help='Request user'),
    )

    def handle(self, *args, **options):
        error_message = ""
        try:
            print "Updating tendenci"
            subprocess.check_output("pip install tendenci --upgrade", stderr=subprocess.STDOUT, shell=True)

            print "Updating tendenci site"
            subprocess.check_output("python deploy.py", stderr=subprocess.STDOUT, shell=True)

            print "Restarting Server"
            subprocess.check_output("sudo reload %s" % os.path.basename(settings.PROJECT_ROOT),
                                    stderr=subprocess.STDOUT, shell=True)

            call_command('clear_cache')
        except subprocess.CalledProcessError as e:
            error_message = e.output
        except CommandError as e:
            error_message = e

        from tendenci import __version__ as version
        from tendenci.apps.notifications import models as notification
        from tendenci.core.site_settings.utils import get_setting

        email_context = {'site_url':get_setting('site', 'global', 'siteurl'),
                         'version':version, 'error_message':error_message}

        recipients = (get_setting('site', 'global', 'allnoticerecipients')).split(',')
        user_id = options['user']
        if User.objects.filter(pk=user_id).exists():
            user = User.objects.get(pk=user_id)
            if user.email:
                recipients.append(user.email)

        email_recipients = list(set(recipients))
        notification.send_emails(email_recipients, 'update_tendenci_notice',
                                 email_context)

