from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = ('Caches the photo for the size on the batch edit page and the photoset view page.')

    def handle(self, *args, **options):
        from tendenci.addons.photos.utils.caching import cache_photo_size

        cache_kwargs_list = []
        cache_kwargs_list.append({"id": args[0], "size": "422x700", "constrain": True})
        cache_kwargs_list.append({"id": args[0], "size": "102x78", "crop": True})
        cache_kwargs_list.append({"id": args[0], "size": "640x640", "constrain": True})

        for cache_kwargs in cache_kwargs_list:
            cache_photo_size(**cache_kwargs)
