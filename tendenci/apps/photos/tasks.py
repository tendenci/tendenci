import os
import zipfile

from django.conf import settings

from celery.task import Task

class ZipPhotoSetTask(Task):

    def run(self, photo_set, **kwargs):
        """
        Compile all photos of a photo set into a single zip file.
        """

        #create zip files directory if it doesn't already exist
        try:
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'zip_files'))
        except OSError:
            pass

        zfile = zipfile.ZipFile(os.path.join(settings.MEDIA_ROOT, 'zip_files', "set_%s.zip" % photo_set.id), 'w')
        for image in photo_set.image_set.all():
            try:
                zfile.write(image.image.path, os.path.basename(image.image.name))
            except OSError:
                # skip missing files
                pass
        zfile.close

        return os.path.join(settings.MEDIA_URL, 'zip_files', "set_%s.zip" % photo_set.id)
