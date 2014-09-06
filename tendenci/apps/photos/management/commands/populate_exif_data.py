from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage

class Command(BaseCommand):
    """
    Populate the exif_data field in Image table.
    """

    def handle(self, *args, **options):
        from tendenci.apps.photos.models import Image

        images = Image.objects.all()
        for image in images:
            if not image.exif_data:
                if default_storage.exists(image.image.name):
                    exif_exists = image.get_exif_data()
                    if exif_exists:
                        image.save()
