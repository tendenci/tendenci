from __future__ import print_function
import time
from datetime import datetime, timedelta
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    Directory export process.

    Usage:
        python manage.py event_export_process

        example:
        python manage.py invoice_export_process --start_dt=2010-10-30
                                                --end_dt=2011-11-30
                                                --identifier=1359048111
                                                --user=1
    """
    option_list = BaseCommand.option_list + (
        make_option(
            '--start_dt',
            action='store',
            dest='start_dt',
            default='',
            help='Export invoices whose update date is greater than or equal to the value specified'),

        make_option(
            '--end_dt',
            action='store',
            dest='end_dt',
            default='',
            help='Export invoices whose update date is less than the value specified'),

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
        from tendenci.apps.invoices.utils import process_invoice_export

        start_dt = options['start_dt']
        end_dt = options['end_dt']
        user_id = options['user']
        identifier = options['identifier']

        if not identifier:
            identifier = int(time.time())

        if start_dt:
            try:
                start_dt = datetime.strptime(start_dt, '%Y-%m-%d')
            except:
                raise CommandError('Please use the following date format YYYY-MM-DD.\n')

        if end_dt:
            try:
                end_dt = datetime.strptime(end_dt, '%Y-%m-%d')
                end_dt = end_dt + timedelta(days=1)
            except:
                raise CommandError('Please use the following date format YYYY-MM-DD.\n')

        process_invoice_export(start_dt=start_dt,
                               end_dt=end_dt,
                               identifier=identifier,
                               user_id=user_id)

        print('Invoice export done %s.' % identifier)

