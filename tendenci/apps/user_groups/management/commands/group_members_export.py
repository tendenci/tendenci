
import time
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Group members or subscribers export.

    Usage:
        python manage.py group_members_export --group_id=xxx

        example:
        # for regular group members
        python manage.py group_members_export --export_target members
                                              --identifier 1370634758
                                              --group_id 1
                                              --user_id 1
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--group_id',
            action='store',
            dest='group_id',
            help='Group id to export')
        parser.add_argument(
            '--export_target',
            action='store',
            dest='export_target',
            default='all',
            help='Export group members or subscribers')
        parser.add_argument(
            '--identifier',
            action='store',
            dest='identifier',
            default='',
            help='Export file identifier')
        parser.add_argument(
            '--user_id',
            action='store',
            dest='user_id',
            default='1',
            help='Request user id')

    def handle(self, *args, **options):
        from tendenci.apps.user_groups.utils import process_export

        group_id = options['group_id']
        if not group_id:
            print('Please specify a group id')
            return

        export_target = options['export_target']
        identifier = options['identifier']

        if not identifier:
            identifier = int(time.time())

        user_id = options['user_id']
        process_export(
            group_id=group_id,
            export_target=export_target,
            identifier=identifier,
            user_id=user_id)

        print('Group members export done %s.' % identifier)
