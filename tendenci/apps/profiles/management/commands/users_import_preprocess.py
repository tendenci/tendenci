
import os
import chardet

from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


class Command(BaseCommand):
    """
    Pre_precess the user import:

        1) Encode the uploaded file.
        2) Dump data to table userimportdata

    Usage:
        python manage.py users_import_preprocess [uimport_id]

        example:
        python manage.py users_import_preprocess 9
    """

    def add_arguments(self, parser):
        parser.add_argument('import_id', type=int)

    def handle(self, *args, **options):
        from tendenci.apps.profiles.models import UserImport, UserImportData
        from tendenci.apps.profiles.utils import user_import_parse_csv

        import_id = options['import_id']
        uimport = get_object_or_404(UserImport,
                                        pk=import_id)
        if uimport.status == 'not_started':
            if uimport.upload_file:
                uimport.status = 'preprocessing'
                uimport.save()

                # encode to utf8 and write to path2
                path2 = '%s_utf8%s' % (os.path.splitext(
                                        uimport.upload_file.name))
                default_storage.save(path2, ContentFile(''))
                f = default_storage.open(uimport.upload_file.name)
                f2 = default_storage.open(path2, 'wb+')
                encoding_updated = False
                for chunk in f.chunks():
                    encoding = chardet.detect(chunk)['encoding']
                    print(encoding)
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
                    uimport.upload_file.file = f2
                    uimport.upload_file.name = f2.name
                    uimport.save()
                else:
                    default_storage.delete(path2)

                # dump data to the table userimportdata
                # note that row_num starts with 2 because the first row
                # is the header row.
                header_line, data_list = user_import_parse_csv(uimport)
                uimport.header_line = ','.join(header_line)

                for i, user_data in enumerate(data_list):

                    import_data = UserImportData(
                                    uimport=uimport,
                                    row_data=user_data,
                                    row_num=i+2)
                    import_data.save()

                uimport.status = 'preprocess_done'
                uimport.save()
