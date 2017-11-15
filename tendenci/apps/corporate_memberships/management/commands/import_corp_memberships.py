from __future__ import print_function
from datetime import datetime
import traceback

from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User


class Command(BaseCommand):
    """
    Import corporate memberships.

    Usage:
        python manage.py import_corp_memberships [mimport_id] [request.user.id]

        example:
        python manage.py import_corp_memberships 10 1
    """
 
    def add_arguments(self, parser):
        parser.add_argument('import_id', type=int)
        parser.add_argument('user_id', type=int)


    def handle(self, *args, **options):
        from tendenci.apps.corporate_memberships.models import CorpMembershipImport
        from tendenci.apps.corporate_memberships.models import CorpMembershipImportData
        from tendenci.apps.corporate_memberships.import_processor import CorpMembershipImportProcessor

        import_id = options['import_id']
        user_id = options['user_id']
        mimport = get_object_or_404(CorpMembershipImport,
                                        pk=import_id)
        request_user = User.objects.get(pk=user_id)

#        fieldnames, data_list = memb_import_parse_csv(mimport)
        data_list = CorpMembershipImportData.objects.filter(
                                mimport=mimport).order_by('pk')

        imd = CorpMembershipImportProcessor(request_user, mimport, dry_run=False)

        for idata in data_list:
            cmemb_data = idata.row_data
            # catch any error
            try:
                imd.process_corp_membership(cmemb_data)
            except Exception as e:
                # mimport.status = 'error'
                # TODO: add a field to log the error
                # mimport.save()
                # raise  Exception(traceback.format_exc())
                print(e)

            mimport.num_processed += 1
            # save the status
            summary = 'insert:%d,update:%d,update_insert:%d,invalid:%d' % (
                                        imd.summary_d['insert'],
                                        imd.summary_d['update'],
                                        imd.summary_d['update_insert'],
                                        imd.summary_d['invalid']
                                        )
            mimport.summary = summary
            mimport.save()

        mimport.status = 'completed'
        mimport.complete_dt = datetime.now()
        mimport.save()
