from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    This command creates a superuser and a profile by allowing you to
    include a password.
    """

    def add_arguments(self, parser):
        parser.add_argument('--username', dest='username', default=None,
            help='Specifies the username for the superuser.')
        parser.add_argument('--email', dest='email', default=None,
            help='Specifies the email address for the superuser.')
        parser.add_argument('--password', dest='password', default=None,
            help='Specifies the password for the superuser.')

    def handle(self, *args, **options):
        username = options.get('username', None)
        email = options.get('email', None)
        password = options.get('password', None)

        if username and email and password:
            from django.contrib.auth.models import User
            from tendenci.apps.profiles.models import Profile

            user = User.objects.create_superuser(username, email, password)
            Profile.objects.create_profile(user)
        else:
            raise CommandError("Username, email, and password are all required.")
