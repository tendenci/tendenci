from django.contrib.contenttypes.models import ContentType
from django.db.models import signals

from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.files.models import File


def save_files(sender, **kwargs):
    # get content type and instance
    content_type = ContentType.objects.get_for_model(sender)
    instance = kwargs['instance']

    orphaned_files = list(File.objects.filter(content_type=content_type, object_id=0))
    coupled_files = list(File.objects.filter(content_type=content_type, object_id=instance.pk))
    files = orphaned_files + coupled_files

    file_ct = ContentType.objects.get_for_model(File)

    perm_attrs = []
    if 'tendencibasemodel' in [s._meta.model_name for s in sender.__bases__ if hasattr(s, '_meta')]:
        # if model (aka sender) inherits from TendenciBaseModel
        perm_attrs = [
            'allow_anonymous_view',
            'allow_user_view',
            'allow_member_view',
            'allow_user_edit',
            'allow_member_edit',
            'status',
            'status_detail',
        ]

    for file in files:  # loop through media files and update

        if not file.object_id:  # pick up orphans
            file.object_id = instance.pk

        # remove all group permissions on file
        ObjectPermission.objects.filter(
            content_type=file_ct, object_id=file.pk, group__isnull=False).delete()

        # get all instance permissions [for copying]
        instance_perms = ObjectPermission.objects.filter(
            content_type=content_type, object_id=instance.pk, group__isnull=False
        )

        # copy instance group permissions to file
        for file_perm in instance_perms:
            file_perm.pk = None
            file_perm.content_type = file_ct
            file_perm.object_id = file.pk
            file_perm.codename = '%s_%s' % (file_perm.codename.split('_')[0], 'file')
            file_perm.save()

        # copy permission attributes
        for attr in perm_attrs:
            # example: file.status = instance.status
            setattr(file, attr, getattr(instance, attr))

        # Update the owner and owner_username since we are
        # updating the update_dt automatically.
        if hasattr(instance, 'owner'):
            file.owner = instance.owner
        if hasattr(instance, 'owner_username'):
            file.owner_username = instance.owner_username
        file.save()


def delete_files(sender, **kwargs):
    from tendenci.apps.files.models import File
    # get content type and instance
    content_type = ContentType.objects.get_for_model(sender)
    instance = kwargs['instance']
    # get orphaned images (images not coupled with application)
    files = File.objects.filter(content_type=content_type, object_id=instance.id)
    # loop through media files and delete
    for file in files:
        file.delete()


def init_signals():
    from tendenci.apps.registry.sites import site
    apps = site.get_registered_apps()

    for app in apps:

        if app['model']._meta.model_name in ('file', 'invoice',):
            continue  # go to next app

        #signals.post_save.connect(save_files, sender=app['model'], weak=False)
        signals.post_delete.connect(delete_files, sender=app['model'], weak=False)
