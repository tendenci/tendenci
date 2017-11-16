from __future__ import print_function
import time
from optparse import make_option
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Article export process.

    Usage:
        python manage.py memberships_export

        example:
        python manage.py membership_export_process --identifier 1359048111
                                                   --user 1

    """ 
    def add_arguments(self, parser):
        parser.add_argument('--identifier',
            dest='identifier',
            default='',
            help='Export file identifier')
        parser.add_argument('--user',
            type=int,
            dest='user',
            default='1',
            help='Request user')

    def handle(self, *args, **options):
        from tendenci.apps.articles.utils import process_export

        identifier = options['identifier']

        if not identifier:
            identifier = int(time.time())

        user_id = options['user']

        process_export(
            identifier=identifier,
            user_id=user_id)

        print('Article export done %s.' % identifier)