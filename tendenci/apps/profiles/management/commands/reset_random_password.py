from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    """
    Reset random password for the specified users

    Usage: manage.py reset_random_password username1 username2 ...
    """

    def add_arguments(self, parser):
        # optional arguments
        parser.add_argument('usernames',
            nargs='*',
            help='one or more usernames')

    def handle(self, usernames, **options):
        from tendenci.apps.base.utils import generate_random_password
        for username in usernames:
            [u] = User.objects.filter(username=username)[:1] or [None]
            if u:
                u.set_password(generate_random_password())
                u.save()
