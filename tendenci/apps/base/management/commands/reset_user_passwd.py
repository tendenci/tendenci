

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):
    """
    Reset password for a given user

    Usage: manage.py reset_user_passwd --username username --password password
    """

    def add_arguments(self, parser):
        parser.add_argument('--username',
            action='store',
            dest='username',
            default=None,
            help='Username whose password being reset')
        parser.add_argument('--password',
            action='store',
            dest='password',
            default=None,
            help='New password being reset for the user')

    def handle(self, *args, **options):
        verbosity = options['verbosity']
        username = options['username']
        password = options['password']

        if not username or not password:
            if not username and not password:
                raise CommandError('reset_user_passwd: --username username and --password password are required')
            elif not username:
                raise CommandError('reset_user_passwd: --username username is required')
            else:
                raise CommandError('reset_user_passwd: --password password is required')

        # get the user
        try:
            u = User.objects.get(username=username)
        except ObjectDoesNotExist:
            print('User with username (%s) could not be found' % username)
            return

        u.set_password(password)
        u.save()

        if verbosity >= 2:
            print('Done reseting password for user (%s).' % u)
