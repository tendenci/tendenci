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
    option_list = BaseCommand.option_list + (

        make_option(
            '--identifier',
            action='store',
            dest='identifier',
            default='',
            help='Export file identifier'),

        make_option(
            '--user',
            action='store',
            dest='user',
            default='1',
            help='Request user'),

    )

    def handle(self, *args, **options):
        from tendenci.addons.articles.utils import process_export

        identifier = options['identifier']

        if not identifier:
            identifier = int(time.time())

        user_id = options['user']

        process_export(
            identifier=identifier,
            user_id=user_id)

        print 'Article export done %s.' % identifier