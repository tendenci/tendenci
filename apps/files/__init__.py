
# django
from django.contrib.contenttypes.models import ContentType
from django.db.models import signals

# local
from files.models import File
from articles.models import Article
from pages.models import Page
from news.models import News
from jobs.models import Job
from directories.models import Directory
from help_files.models import HelpFile
from stories.models import Story


def bind_files(sender, **kwargs):
    # get content type and instance
    content_type = ContentType.objects.get_for_model(sender)
    instance = kwargs['instance']
    # get orphaned files (files not coupled with an application)
    files = File.objects.filter(content_type=content_type, object_id = 0)
    # loop through media files and update
    for file in files:
        file.object_id = instance.id
        file.save()

signals.post_save.connect(bind_files, sender=Page, weak=False)
signals.post_save.connect(bind_files, sender=News, weak=False)
signals.post_save.connect(bind_files, sender=Article, weak=False)
signals.post_save.connect(bind_files, sender=Directory, weak=False)
signals.post_save.connect(bind_files, sender=HelpFile, weak=False)
signals.post_save.connect(bind_files, sender=Story, weak=False)

def delete_files(sender, **kwargs):
    # get content type and instance
    content_type = ContentType.objects.get_for_model(sender)
    instance = kwargs['instance']
    # get orphaned images (images not coupled with application)
    files = File.objects.filter(content_type=content_type, object_id = instance.id)
    # loop through media files and delete
    for file in files:
        file.delete()

signals.post_delete.connect(delete_files, sender=Page, weak=False)
signals.post_delete.connect(delete_files, sender=News, weak=False)
signals.post_delete.connect(delete_files, sender=Article, weak=False)
signals.post_delete.connect(delete_files, sender=Directory, weak=False)
signals.post_delete.connect(delete_files, sender=HelpFile, weak=False)
signals.post_delete.connect(delete_files, sender=Story, weak=False)