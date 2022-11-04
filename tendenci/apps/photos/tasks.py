import os
import zipfile

from django.conf import settings

import celery

class ZipPhotoSetTask(celery.Task):

    def run(self, photo_set, **kwargs):
        """
        Compile all photos of a photo set into a single zip file.
        """
        #TODO: make it work with default_storage (such as s3)
        zip_file_name = f"set_{photo_set.id}.zip"
        zip_file_directory = 'export/zip_files'
        zip_file_path = os.path.join(settings.MEDIA_ROOT, zip_file_directory)
        zip_file_full_path = os.path.join(zip_file_path, zip_file_name)

        #create zip files directory if it doesn't already exist
        try:
            os.makedirs(zip_file_path)
        except OSError:
            pass

        zfile = zipfile.ZipFile(zip_file_full_path, 'w')
        for image in photo_set.image_set.all():
            try:
                zfile.write(image.image.path, os.path.basename(image.image.name))
            except OSError:
                # skip missing files
                pass
        zfile.close

        return os.path.join(settings.MEDIA_URL, zip_file_directory, zip_file_name)
