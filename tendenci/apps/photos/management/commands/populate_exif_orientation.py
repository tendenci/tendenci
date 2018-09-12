from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from PIL import Image as PILImage
from PIL.ExifTags import TAGS as PILTAGS

class Command(BaseCommand):
    """
    Extract and assign Orientation to exif_data.
    Orientation is not previously populated in the exif_data.
    """

    def handle(self, *args, **options):
        from tendenci.apps.photos.models import Image

        photos = Image.objects.all()
        for photo in photos:
            if photo.exif_data and not photo.exif_data.get('Orientation'):
                try:
                    img = PILImage.open(default_storage.open(photo.image.name))
                    exif = img._getexif()
                    if exif:
                        for tag, value in exif.items():
                            key = PILTAGS.get(tag, tag)
                            if key == 'Orientation':
                                photo.exif_data[key] = value
                                photo.save()
                                break
                except (AttributeError, IOError):
                    pass

