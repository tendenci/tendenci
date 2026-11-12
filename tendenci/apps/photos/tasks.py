import os
import zipfile
import tempfile

from django.core.files.storage import default_storage
from django.core.files.base import File

import celery

class ZipPhotoSetTask(celery.Task):

    def run(self, photo_set, identifier, **kwargs):
        """
        Compile all photos of a photo set into a single zip file.
        """
        zip_file_relative_path = photo_set.get_export_zip_file_path(identifier)

        storage_backend = default_storage.__class__.__name__
        
        with tempfile.TemporaryFile() as temp_zip:
            with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zfile:
                for image in photo_set.image_set.all():
                    print('image.image.path=', image.image.name)
                    if default_storage.exists(image.image.name):
                        if storage_backend == "FileSystemStorage":
                            # on local file system
                            zfile.write(image.image.path, os.path.basename(image.image.name))
                        else:
                            # on remote cloud provider
                            with default_storage.open(image.image.name, "rb") as extracted_file:
                                file_content = extracted_file.read()
                            zfile.writestr(os.path.basename(image.image.name), file_content)
            # Rewind the temporary file pointer before saving to default_storage
            temp_zip.seek(0)
            saved_path = default_storage.save(zip_file_relative_path, File(temp_zip))

        return identifier
