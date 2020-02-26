
import time
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Profile export process.

    Usage:
        python manage.py directory_export_process

        example:
        python manage.py profile_export_process --export_fields=main_fields
                                                --identifier=1359048111
                                                --user=1
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--export_fields',
            action='store',
            dest='export_fields',
            default='main_fields',
            help='Either main_fields or all_fields to export')
        parser.add_argument(
            '--identifier',
            action='store',
            dest='identifier',
            default='',
            help='Export file identifier')
        parser.add_argument(
            '--user',
            action='store',
            dest='user',
            default='1',
            help='Request user')

    def handle(self, *args, **options):
        from tendenci.apps.profiles.utils import process_export

        export_fields = options['export_fields']
        user_id = options['user']
        identifier = options['identifier']

        if not identifier:
            identifier = int(time.time())

        process_export(
            export_fields=export_fields,
            identifier=identifier,
            user_id=user_id)

        print('Profile export done %s.' % identifier)
