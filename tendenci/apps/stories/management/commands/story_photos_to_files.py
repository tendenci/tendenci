import os
import shutil
import commands
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """
    example: python manage.py story_photos_to_files.py
    """
    def handle(self, *args, **kwargs):
        from tendenci.apps.stories.models import Story, StoryPhoto

        status, output = commands.getstatusoutput('sudo chown -R ubuntu:www-data %s' % settings.MEDIA_ROOT)
        if status > 0:
            print output
            return

        stories = Story.objects.all()
        for story in stories:
            try:
                photo = story.photo
                file = photo.file

            except (ValueError, IOError) as e:
                file = None

            if file:
                src = photo.path
                dest = photo.path.replace(settings.MEDIA_ROOT + '/stories', settings.MEDIA_ROOT + '/files/stories')
                if src != dest:
                    print "Moving %s to %s" % (src, dest)
                    dir = os.path.dirname(dest)
                    if not os.path.exists(dir):
                        os.makedirs(dir)

                    shutil.move(src, dest)
                    story.photo.save(dest.replace(settings.MEDIA_ROOT + '/files/stories/', ''), File(open(dest)))
                    story.save()
                print "Creating StoryPhoto %s for %s" % (dest, story.title)
                image = StoryPhoto(
                    creator = story.creator,
                    creator_username = story.creator_username,
                    owner = story.owner,
                    owner_username = story.owner_username)
                image.file.save(dest.replace(settings.MEDIA_ROOT + '/files/stories/', ''), File(open(dest)))
                image.save()
                if story.image:
                    old_image = story.image
                    story.image = None
                    story.save()
                    old_image.delete()
                story.image = image
                story.save()
