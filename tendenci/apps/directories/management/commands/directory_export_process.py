
import time
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Directory export process.

    Usage:
        python manage.py directory_export_process

        example:
        python manage.py directory_export_process --export_fields=main_fields
                                                  --export_status_detail=active
                                                  --identifier=1359048111
                                                  --user=1
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--export_status_detail',
            action='store',
            dest='export_status_detail',
            default='',
            help='Export directories with the status detail specified')
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
        from tendenci.apps.directories.utils import process_export

        export_fields = options['export_fields']
        export_status_detail = options['export_status_detail']
        user_id = options['user']
        identifier = options['identifier']

        if not identifier:
            identifier = int(time.time())

        process_export(
            export_fields=export_fields,
            export_status_detail=export_status_detail,
            identifier=identifier,
            user_id=user_id)

        print('Directory export done %s.' % identifier)
