from django.contrib.contenttypes.models import ContentType
from django.db.models import signals
from files.models import File

def save_files(sender, **kwargs):
    from django.contrib.sessions.models import Session

    # get content type and instance
    content_type = ContentType.objects.get_for_model(sender)
    instance = kwargs['instance']

    orphaned_files = list(File.objects.filter(content_type=content_type, object_id=0))
    coupled_files = list(File.objects.filter(content_type=content_type, object_id=instance.pk))
    files = orphaned_files + coupled_files

    perm_attrs = []
    if 'tendencibasemodel' in [s._meta.module_name for s in sender.__bases__ if hasattr(s,'_meta')]:
        # if model (aka sender) inherits from TendenciBaseModel
        perm_attrs = [
            'allow_anonymous_view',
            'allow_user_view',
            'allow_member_view',
            'allow_anonymous_edit',
            'allow_user_edit',
            'allow_member_edit',
            'status',
            'status_detail',
        ]

    for file in files:  # loop through media files and update

        if not file.object_id:  # pick up orphans
            file.object_id = instance.pk

        for attr in perm_attrs:
            # example: file.status = instance.status
            setattr(file, attr, getattr(instance, attr))
        file.name = file.file.path.split('/')[-1]

        file.save()

def delete_files(sender, **kwargs):
    from files.models import File
    # get content type and instance
    content_type = ContentType.objects.get_for_model(sender)
    instance = kwargs['instance']
    # get orphaned images (images not coupled with application)
    files = File.objects.filter(content_type=content_type, object_id = instance.id)
    # loop through media files and delete
    for file in files:
        file.delete()


def init_signals():
    from registry import site
    apps = site.get_registered_apps()

    for app in apps:

        if app['model']._meta.module_name in ('file', 'invoice',):
            continue  # go to next app

        signals.post_save.connect(save_files, sender=app['model'], weak=False)
        signals.post_delete.connect(delete_files, sender=app['model'], weak=False)