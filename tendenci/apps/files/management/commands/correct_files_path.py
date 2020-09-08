
import re
import os

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command


class Command(BaseCommand):
    """
    Correct files path based on their content types. For example, instead of being uploaded to
    files/files/, files with page content type should go to files/page/...


        python manage.py correct_files_path
    """

    def handle(self, *apps, **kwargs):
        from tendenci.apps.files.models import File as tFile

        p = r'^files/files/'

        files = tFile.objects.filter(status_detail='active')
        for f in files:
            if f.file and f.content_type:
                if re.compile(p).search(f.file.name):
                    file_name_from = f.file.name
                    content_type = str(f.content_type)
                    content_type = re.sub(r'[^a-zA-Z0-9._]+', '-', str(content_type))
                    content_type = content_type.lower()
                    file_name_to = re.sub(p, 'files/{}/'.format(content_type), f.file.name)

                    file_full_path_from = os.path.join(settings.MEDIA_ROOT, file_name_from)
                    file_full_path_to = os.path.join(settings.MEDIA_ROOT, file_name_to)
                    if os.path.isfile(file_full_path_from):
                        print('from: ', file_name_from, 'to: ', file_name_to)
                        os.renames(file_full_path_from, file_full_path_to)
                    
                        f.file.name = file_name_to
                        f.save()

        # clear cache
        call_command('clear_cache')
        print('Done')
