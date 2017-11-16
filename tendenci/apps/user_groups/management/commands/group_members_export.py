from __future__ import print_function
import time
from optparse import make_option
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
    option_list = BaseCommand.option_list + (

        make_option(
            '--group_id',
            action='store',
            dest='group_id',
            help='Group id to export'),

        make_option(
            '--export_target',
            action='store',
            dest='export_target',
            default='all',
            help='Export group members or subscribers'),

        make_option(
            '--identifier',
            action='store',
            dest='identifier',
            default='',
            help='Export file identifier'),

        make_option(
            '--user_id',
            action='store',
            dest='user_id',
            default='1',
            help='Request user id'),
    )

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
