from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Insert non-profit-organization default data"

    def handle(self, **options):

        suffix_list = [
            'auth_user',
            'profiles_profile',
            'entities',
            'user_groups',
            'events',
            'jobs',
            'memberships',
            'memberships_membershipdefault',
            'news',
            'photos',
            'boxes',
            'navs',
            'pages',
            'stories',
        ]

        # call loaddata on fixtures
        for suffix in suffix_list:
            filename = 'npo_default_%s.json' % suffix

            print filename
            call_command('loaddata', filename)
