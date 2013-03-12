import time
from optparse import make_option

from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
#from django.contrib.auth.models import User


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
    """
    option_list = BaseCommand.option_list + (
        make_option('--export_type',
            action='store',
            dest='export_type',
            default='main_fields',
            help='Either main_fields or all_fields to export'),
        make_option('--export_status_detail',
            action='store',
            dest='export_status_detail',
            default='active',
            help='Export memberships with the status detail specified'),
        make_option('--identifier',
            action='store',
            dest='identifier',
            default='',
            help='Export file identifier'),
        make_option('--user',
            action='store',
            dest='user',
            default='1',
            help='Request user'),
        )

    def handle(self, *args, **options):
        from tendenci.addons.memberships.utils import process_export
        from tendenci.core.site_settings.utils import get_setting
        export_type = options['export_type']
        export_status_detail = options['export_status_detail']
        identifier = options['identifier']
        if not identifier:
            identifier = int(time.time())
        #user = options['user']
        process_export(export_type=export_type,
                       export_status_detail=export_status_detail,
                       identifier=identifier)
        print 'Membership export done %s.' % identifier
#        print 'URL to download: ', '%s%s' % (get_setting('site', 'global',
#                                                         'siteurl'),
#            reverse('memberships.default_export_download', args=[identifier]))
