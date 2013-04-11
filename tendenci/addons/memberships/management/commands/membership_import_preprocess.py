import os
import chardet
import traceback

from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


class Command(BaseCommand):
    """
    Pre_precess the membership import:

        1) Encode the uploaded file.
        2) Dump data to table membershipimportdata

    Usage:
        python manage.py membership_import_preprocess [mimport_id]

        example:
        python manage.py membership_import_preprocess 56
    """

    def handle(self, *args, **options):
        from tendenci.addons.memberships.models import MembershipImport
        from tendenci.addons.memberships.models import MembershipImportData
        from tendenci.addons.memberships.utils import memb_import_parse_csv

        mimport = get_object_or_404(MembershipImport,
                                        pk=args[0])
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

                # dump data to the table membershipimportdata
                # note that row_num starts with 2 because the first row
                # is the header row.
                header_line, data_list = memb_import_parse_csv(mimport)
                mimport.header_line = ','.join(header_line)

                for i, memb_data in enumerate(data_list):

                    import_data = MembershipImportData(
                                    mimport=mimport,
                                    row_data=memb_data,
                                    row_num=i+2)
                    import_data.save()

                mimport.status = 'preprocess_done'
                mimport.save()
