import time
from optparse import make_option
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Membership export process.

    Usage:
        python manage.py membership_export_process

        example:
        python manage.py membership_export_process --export_type main_fields
                                                   --export_status_detail active
                                                   --identifier 1359048111
                                                   --user 1
                                                   --cp_id 21
    """
    option_list = BaseCommand.option_list + (

        make_option(
            '--export_status_detail',
            action='store',
            dest='export_status_detail',
            default='active',
            help='Export memberships with the status detail specified'),

        make_option(
            '--export_fields',
            action='store',
            dest='export_fields',
            default='main_fields',
            help='Either main_fields or all_fields to export'),

        make_option(
            '--export_type',
            action='store',
            dest='export_type',
            default='all',
            help='All or one specific membership type'),

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

        make_option(
            '--cp_id',
            action='store',
            dest='cp_id',
            default=0,
            help='corp_profile id'),

    )

    def handle(self, *args, **options):
        from tendenci.addons.memberships.utils import process_export

        export_fields = options.get('export_fields', 'main_fields')
        export_type = options.get('export_type', 'all')
        export_status_detail = options.get('export_status_detail', 'active')
        identifier = options.get('identifier', None)

        if not identifier:
            identifier = int(time.time())

        cp_id = int(options.get('cp_id', 0)) or 0

        user_id = options.get('user', '1')
        process_export(
            export_fields=export_fields,
            export_type=export_type,
            export_status_detail=export_status_detail,
            identifier=identifier,
            user_id=user_id,
            cp_id=cp_id)

        print 'Membership export done %s.' % identifier
