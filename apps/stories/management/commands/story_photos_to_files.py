import shutil
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """
    example: python manage.py story_photos_to_files.py
    """
    def handle(self, *args, **kwargs):
        from stories.models import Story
        stories = Story.objects.all()
        for story in stories:
            try:
                photo = story.photo
                file = photo.file
            except IOError:
                file = None
            if file:
                src = file.name
                dest = file.name.replace(settings.MEDIA_ROOT + '/stories', settings.MEDIA_ROOT + '/files/stories')
                shutil.move(src, dest)
                story.photo.save(dest.replace(settings.MEDIA_ROOT + '/files/stories', ''), File(open(dest)))
                story.save()
