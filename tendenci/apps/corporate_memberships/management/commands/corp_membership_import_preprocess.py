import os
import chardet

from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


class Command(BaseCommand):
    """
    Pre_precess the corporate membership import:

        1) Encode the uploaded file.
        2) Dump data to table CorpMembershipImportData

    Usage:
        python manage.py corp_membership_import_preprocess [mimport_id]

        example:
        python manage.py corp_membership_import_preprocess 1
    """

    def add_arguments(self, parser):
        parser.add_argument('import_id', type=int)

    def handle(self, *args, **options):
        from tendenci.apps.corporate_memberships.models import CorpMembershipImport
        from tendenci.apps.corporate_memberships.models import CorpMembershipImportData
        from tendenci.apps.memberships.utils import memb_import_parse_csv

        mimport = get_object_or_404(CorpMembershipImport,
                                        pk=options['import_id'])
        if mimport.status == 'not_started':
            if mimport.upload_file:
                mimport.status = 'preprocessing'
                mimport.save()

                # encode to utf8 and write to path2
                path2 = '%s_utf8%s' % (os.path.splitext(
                                        mimport.upload_file.name))
                default_storage.save(path2, ContentFile(''))
                f = default_storage.open(mimport.upload_file.name)
                f2 = default_storage.open(path2, 'wb+')
                encoding_updated = False
                for chunk in f.chunks():
                    encoding = chardet.detect(chunk)['encoding']
                    if encoding not in ('ascii', 'utf8'):
                        if encoding == 'ISO-8859-1' or \
                            encoding == 'ISO-8859-2':
                            encoding = 'latin-1'
                        chunk = chunk.decode(encoding)
                        chunk = chunk.encode('utf8')
                        encoding_updated = True
                    f2.write(chunk)
                f2.close()
                if encoding_updated:
                    mimport.upload_file.file = f2
                    mimport.upload_file.name = f2.name
                    mimport.save()
                else:
                    default_storage.delete(path2)

                # dump data to the table CorpMembershipImportData
                # note that row_num starts with 2 because the first row
                # is the header row.
                data_list = memb_import_parse_csv(mimport)[1]
                for i, memb_data in enumerate(data_list):

                    import_data = CorpMembershipImportData(
                                    mimport=mimport,
                                    row_data=memb_data,
                                    row_num=i+2)
                    import_data.save()

                mimport.status = 'preprocess_done'
                mimport.save()
