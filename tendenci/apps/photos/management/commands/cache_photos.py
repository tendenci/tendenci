from __future__ import print_function
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = ('Loops through all of the photos to create a cached version.')

    def handle(self, *args, **options):
        from tendenci.apps.photos.models import Image
        from tendenci.apps.photos.utils.caching import cache_photo_size

        for photo in Image.objects.all().order_by('-pk'):

            cache_kwargs_list = []
            cache_kwargs_list.append({"id": photo.pk, "size": "422x700", "constrain": True})
            cache_kwargs_list.append({"id": photo.pk, "size": "102x78", "crop": True})
            cache_kwargs_list.append({"id": photo.pk, "size": "640x640", "constrain": True})

            for cache_kwargs in cache_kwargs_list:
                cache_photo_size(**cache_kwargs)

            print(photo.pk)
