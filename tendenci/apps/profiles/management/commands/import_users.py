from datetime import datetime
import traceback
from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User


class Command(BaseCommand):
    """
    Import users.

    Usage:
        python manage.py import_users [mimport_id] [request.user.id]

        example:
        python manage.py import_users 10 1
    """


    def add_arguments(self, parser):
        parser.add_argument('import_id', type=int)
        parser.add_argument('user_id', type=int)

    def handle(self, *args, **options):
        from tendenci.apps.profiles.models import UserImport, UserImportData
        from tendenci.apps.profiles.utils import ImportUsers
        from tendenci.apps.user_groups.models import GroupMembership

        import_id = options['import_id']
        user_id = options['user_id']
        uimport = get_object_or_404(UserImport, pk=import_id)
        request_user = User.objects.get(pk=user_id)
        data_list = UserImportData.objects.filter(uimport=uimport).order_by('pk')
        imu = ImportUsers(request_user, uimport, dry_run=False)

        # clear group if needed
        if uimport.group_id and uimport.clear_group_membership:
            GroupMembership.objects.filter(group_id=uimport.group_id).delete()


        for idata in data_list:
            try:
                imu.process_user(idata)
            except Exception, e:
                print traceback.format_exc()

            uimport.num_processed += 1

            # save the status -----------------------------------------------
            summary = 'insert:%d,update:%d,invalid:%d' % (
                imu.summary_d['insert'],
                imu.summary_d['update'],
                imu.summary_d['invalid'],
            )
            uimport.summary = summary
            uimport.save()

        uimport.status = 'completed'
        uimport.complete_dt = datetime.now()
        uimport.save()

        # generate a recap file
        uimport.generate_recap()

