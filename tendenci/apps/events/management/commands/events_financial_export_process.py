
import time
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Events financial export process.

    Usage:
        python manage.py events_financial_export_process

        example:
        python manage.py events_financial_export_process --identifier=234321112 \
                                                --user=1 \
                                                --start_dt="2019-01-01 08:00:00" \
                                                --end_dt="2019-02-01 00:00:00" \
                                                --sort_by="start_dt" \
                                                --sort_direction="-"
    """

    def add_arguments(self, parser):
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
        parser.add_argument(
            '--start_dt',
            action='store',
            dest='start_dt',
            default='',
            help='Start date')
        parser.add_argument(
            '--end_dt',
            action='store',
            dest='end_dt',
            default='',
            help='End date')
        parser.add_argument(
            '--sort_by',
            action='store',
            dest='sort_by',
            default='',
            help='Sort by')
        parser.add_argument(
            '--sort_direction',
            action='store',
            dest='sort_direction',
            default='',
            help='Sort direction')

    def handle(self, *args, **options):
        from tendenci.apps.events.utils import do_events_financial_export
        
        identifier = options['identifier']
        if not identifier:
            identifier = int(time.time())

        user_id = options['user']
        start_dt = options['start_dt']
        end_dt = options['end_dt']
        sort_by = options['sort_by']
        sort_direction = options['sort_direction']

        do_events_financial_export(
            identifier=identifier,
            start_dt=start_dt,
            end_dt=end_dt,
            sort_by=sort_by,
            sort_direction=sort_direction,
            user_id=user_id,
            )
 
        print('Event financial export done %s.' % identifier)
