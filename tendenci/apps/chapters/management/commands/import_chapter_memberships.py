
from datetime import datetime

from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User


class Command(BaseCommand):
    """
    Import Chapter Memberships.

    Usage:
        python manage.py import_chapter_memberships [mimport_id] [request.user.id]

        Example:
        python manage.py import_chapter_memberships 10 1
    """
    def add_arguments(self, parser):
        parser.add_argument('import_id', type=int)
        parser.add_argument('user_id', type=int)

    def handle(self, *args,  **options):
        from tendenci.apps.chapters.models import ChapterMembershipImport, ChapterMembershipImportData
        from tendenci.apps.chapters.utils import ImportChapterMembership

        import_id = options['import_id']
        user_id = options['user_id']
        mimport = get_object_or_404(ChapterMembershipImport, pk=import_id)
        request_user = User.objects.get(pk=user_id)
        data_list = ChapterMembershipImportData.objects.filter(mimport=mimport).order_by('pk')
        imd = ImportChapterMembership(request_user, mimport, dry_run=False)

        for idata in data_list:
            try:
                imd.process_chapter_membership(idata)
            except Exception as e:
                print(e)

            mimport.num_processed += 1

            # save the status -----------------------------------------------
            summary = 'insert:%d,update:%d,update_insert:%d,invalid:%d' % (
                imd.summary_d['insert'],
                imd.summary_d['update'],
                imd.summary_d['update_insert'],
                imd.summary_d['invalid'],
            )
            mimport.summary = summary
            mimport.save()

        mimport.status = 'completed'
        mimport.complete_dt = datetime.now()
        mimport.save()

        # generate a recap file
        mimport.generate_recap()
