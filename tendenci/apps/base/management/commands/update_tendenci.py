import os
import subprocess
from xmlrpc import client as xmlrpc_client

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail.message import EmailMessage
from django.core.management.base import BaseCommand
from django.core.management import call_command, CommandError
from django.template.loader import render_to_string

from tendenci.libs.utils import python_executable


class Command(BaseCommand):
    """
    Update tendenci via pip and restarts the server
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            action='store',
            dest='user',
            default='',
            help='Request user')

    def handle(self, *args, **options):
        from tendenci.apps.site_settings.utils import get_setting

        pass_update_tendenci = False
        pass_update_tendenci_site = False
        is_uwsgi = False
        gunicorn_error_msg = None
        uwsgi_error_msg = None
        errors_list = []

        pypi = xmlrpc_client.ServerProxy('http://pypi.python.org/pypi')
        latest_version = pypi.package_releases('tendenci')[0]
        error_message = ""
        email_context = {'site_url':get_setting('site', 'global', 'siteurl'),
                         'version':latest_version, 'error_message':error_message}

        email_sender = get_setting('site', 'global', 'siteemailnoreplyaddress') or settings.DEFAULT_FROM_EMAIL
        email_recipient = ""
        user_id = options['user']
        if user_id and User.objects.filter(pk=user_id).exists():
            user = User.objects.get(pk=user_id)
            if user.email:
                email_recipient = user.email

        try:
            print("Updating tendenci")
            output = subprocess.check_output("%s -m pip install -r requirements/tendenci.txt --upgrade" % python_executable(), stderr=subprocess.STDOUT, shell=True)
            print(output.decode())
            pass_update_tendenci = True

        except subprocess.CalledProcessError as e:
            errors_list.append(e.output.decode())

        # run deploy iff update_tendenci is successful
        if pass_update_tendenci:
            try:
                print("Updating tendenci site")
                call_command('migrate')
                call_command('deploy')
                pass_update_tendenci_site = True
            except CommandError as e:
                errors_list.append(e.output)

        # run reload if update is done
        if pass_update_tendenci_site:
            try:
                print("Restarting Server")
                subprocess.check_output("sudo systemctl restart %s" % os.path.basename(settings.PROJECT_ROOT),
                                    stderr=subprocess.STDOUT, shell=True)

            except subprocess.CalledProcessError as e:
                gunicorn_error_msg = e.output.decode()
                if "reload: Unknown job:" in e.output.decode():
                    is_uwsgi = True

        # run usgi command iff it was proven that the site is using uwsgi instead
        if is_uwsgi:
            try:
                print("Restarting Server")
                subprocess.check_output("sudo touch /etc/uwsgi/vassals/%s.ini" % os.path.basename(settings.PROJECT_ROOT),
                                    stderr=subprocess.STDOUT, shell=True)

            except subprocess.CalledProcessError as e:
                uwsgi_error_msg = e.output.decode()

        if gunicorn_error_msg and uwsgi_error_msg:
            errors_list.append(uwsgi_error_msg)
            errors_list.append(gunicorn_error_msg)

        try:
            print("Clearing cache")
            call_command('clear_cache')
        except CommandError as e:
            errors_list.append(e.output)

        email_context['errors_list'] = errors_list

        if email_recipient:
            subject = render_to_string(template_name='notification/update_tendenci_notice/short.txt', context=email_context)
            subject = subject.strip('\n').strip('\r')
            body = render_to_string(template_name='notification/update_tendenci_notice/full.html', context=email_context)
            email = EmailMessage()
            email.subject = subject
            email.body = body
            email.from_email = email_sender
            email.to = [email_recipient]
            email.content_subtype = 'html'
            email.send()
        else:
            for err in errors_list:
                print(err)
