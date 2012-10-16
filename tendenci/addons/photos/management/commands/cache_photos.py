from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = ('Loops through all of the photos to create a cached version.')

    def handle(self, *args, **options):
        from tendenci.addons.photos.models import Image

        for photo in Image.objects.all().order_by('-pk'):

            print photo.id, photo.get_display_url()
            print photo.id, photo.get_medium_640_url()
