import os
import subprocess

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail.message import EmailMessage
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from tendenci.libs.utils import python_executable


class Command(BaseCommand):
    """
    Update tendenci to the latest version.

    Usage:
        python manage.py auto_update --user_id=1 --verbosity=2
    """

    def add_arguments(self, parser):
        parser.add_argument('--user_id', type=int)

    def handle(self, *args, **options):
        from tendenci.apps.site_settings.utils import get_setting
        from tendenci import __version__ as version
        from tendenci.apps.base.utils import get_latest_version

        verbosity = int(options['verbosity'])
        user_id = options['user_id']
        if user_id:
            [request_user] = User.objects.filter(pk=user_id)[:1] or [None]
        else:
            request_user = None
        site_url = get_setting('site', 'global', 'siteurl')

        # check what tendenci version we're on
        major_bit = int(version.split('.')[0])
        if major_bit < 7:
            if verbosity >1:
                print("No update for this version {}.".format(version))
                print("Please consider to upgrade https://tendenci.readthedocs.org/en/latest/")
            return

        project_root = settings.PROJECT_ROOT
        err_list = []

        # check the latest version
        latest_version = get_latest_version()
        if int(latest_version.split('.')[0]) < 7 or  version == latest_version:
            # STOP - NO UPDATE
            return
        if verbosity >1:
            print("Latest version: {}".format(latest_version))
            print("Your version: {}".format(version))
            print("Start updating...")

        # update requirements/tendenci.txt
        files_to_update = {'requirements/tendenci.txt': 'https://raw.githubusercontent.com/tendenci/tendenci-project-template/master/requirements/tendenci.txt'}
        for key, value in files_to_update.items():
            try:
                subprocess.check_output('curl {0} > {1}/{2}'.format(value, project_root, key),
                                        stderr=subprocess.STDOUT, shell=True)
            except subprocess.CalledProcessError as e:
                err_list.append(e.output)

        # update tendenci
        if not err_list:
            try:
                if verbosity >1:
                    print("Updating tendenci...")
                update_cmd = '{0} -m pip install -r {1}/{2} --upgrade'.format(python_executable(), project_root, 'requirements/tendenci.txt')
                subprocess.check_output('cd {}; {}'.format(project_root, update_cmd),
                                        stderr=subprocess.STDOUT, shell=True)
            except subprocess.CalledProcessError as e:
                err_list.append(e.output)

        if not err_list:
            # run migrate
            try:
                subprocess.check_output("cd {0}; {1} manage.py migrate".format(latest_version, python_executable()),

                                        stderr=subprocess.STDOUT, shell=True)
            except subprocess.CalledProcessError as e:
                known_error = "BadMigrationError: Migrated app 'djcelery' contains South migrations"
                known_error2 = 'relation "djcelery_crontabschedule" already exists'
                if known_error in e.output or known_error2 in e.output:
                    try:
                        subprocess.check_output("cd {0}; {1} manage.py migrate djcelery 0001 --fake".format(latest_version, python_executable()),
                                            stderr=subprocess.STDOUT, shell=True)
                        subprocess.check_output("cd {0}; {1} manage.py migrate".format(latest_version, python_executable()),
                                            stderr=subprocess.STDOUT, shell=True)
                    except subprocess.CalledProcessError as e:
                        err_list.append(e.output)
        if not err_list:
            # run collectstatic, etc via deploy
            try:
                call_command('deploy')
            except CommandError as e:
                err_list.append(e.output)

        if not err_list:
            if verbosity >1:
                print('Reloading the site...')
            # reload the site.
            # it's a guessing game here - because we don't know what wsgi server the site is behind
            # and how exactly the site was set up
            try:
                subprocess.check_output("sudo reload %s" % os.path.basename(settings.PROJECT_ROOT),
                                        stderr=subprocess.STDOUT, shell=True)
            except subprocess.CalledProcessError as e:
                try:
                    subprocess.check_output("sudo sv kill tendenci_site && sv start tendenci_site",
                                            stderr=subprocess.STDOUT, shell=True)
                except subprocess.CalledProcessError as e:
                    err_list.append(e.output)

        if verbosity >1:
            if err_list:
                print('Sorry, updating tendenci is not complete due to the following error(s):\n\n')
                print('\n\n'.join(err_list))
            else:
                print("Update is done.")

        if request_user and request_user.email:
            # notify update is done
            if err_list:
                subject = 'Error on updating tendenci %s' % site_url
                body = 'Error(s) encountered on updating tendenci:\n\n'
                body += '\n\n'.join(err_list)
            else:
                subject = 'Update tendenci is done %s' % site_url
                body = 'Successfully updated tendenci for %s.\n\n' % site_url
                body += 'Tendenci version: %s\n\n' % latest_version
            body += "Thanks!\n%s\n\n" % get_setting('site', 'global', 'sitedisplayname')

            msg = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [request_user.email])
            msg.send()
