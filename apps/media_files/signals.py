
# django
from django.contrib.contenttypes.models import ContentType
from django.db.models import signals

# local
from media_files.models import MediaFile
from articles.models import Article
from pages.models import Page

def bind_wysiwyg_images(sender, **kwargs):
    # get content type and instance
    content_type = ContentType.objects.get_for_model(sender)
    instance = kwargs['instance']
    # get orphaned images (images not coupled with application)
    media_files = MediaFile.objects.filter(application=content_type, application_instance_id = 0)
    # loop through media files and update
    for media_file in media_files:
        media_file.application_instance_id = instance.id
        media_file.save()

signals.post_save.connect(bind_wysiwyg_images, sender=Page, weak=False)
signals.post_save.connect(bind_wysiwyg_images, sender=Article, weak=False)

def delete_media_files(sender, **kwargs):
    # get content type and instance
    content_type = ContentType.objects.get_for_model(sender)
    instance = kwargs['instance']
    # get orphaned images (images not coupled with application)
    media_files = MediaFile.objects.filter(application=content_type, application_instance_id = instance.id)
    # loop through media files and delete
    for media_file in media_files:
        media_file.delete()

signals.post_delete.connect(delete_media_files, sender=Page, weak=False)
signals.post_delete.connect(delete_media_files, sender=Article, weak=False)