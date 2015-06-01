import os
import re
from datetime import datetime
from haystack.query import SearchQuerySet

from django.contrib.contenttypes.models import ContentType
from django.db.models import Manager
from django.conf import settings
from django.core.files.storage import default_storage

from tendenci.apps.perms.managers import TendenciBaseManager


def save_to_disk(f, instance):
    """
    Takes file object and instance (or model).
    Returns back relative path of file.
    """
    file_name = re.sub(r'[^a-zA-Z0-9._-]+', '_', f.name)

    # make dir with app and module name
    relative_directory = os.path.join(
        'files',
        instance._meta.app_label,
        instance._meta.model_name,
    )

    # make directory with pk
    if isinstance(instance.pk, (int, long)):
        relative_directory = os.path.join(
            relative_directory,
            unicode(instance.pk))

    default_storage.save(os.path.join(relative_directory, file_name), f)

#    absolute_directory = os.path.join(settings.MEDIA_ROOT, relative_directory)
#
#    if not os.path.exists(absolute_directory):
#        os.makedirs(absolute_directory)
#
#    destination = open(os.path.join(absolute_directory, file_name), 'wb+')
#    for chunk in f.chunks():
#        destination.write(chunk)
#    destination.close()

    # relative path
    return os.path.join(relative_directory, file_name)

class FileManager(TendenciBaseManager):
    """
    Model Manager
    """

    def get_for_model(self, instance):
        return self.model.objects.filter(
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.pk,
        )

    def bind_files_to_instance(self, files, instance, **kwargs):
        """
        Save files and associate with instance.
        Return list of files saved.
        """
        from django.contrib.auth.models import User

        try:  # explicit user; default to admin
            user = kwargs.get('user') or User.objects.get(id=1)
        except User.DoesNotExist as e:
            return []

        # loop; save file; save file record in db
        # ----------------------------------------

        files_saved = []
        for file in files:

            # what to save; where to save it
            file.file.seek(0)
            file_path = save_to_disk(file, instance)

            # update file record; or create new file record
            # ----------------------------------------------

            instance_pk = None
            if isinstance(instance.pk, long):
                instance_pk = instance.pk

            try:
                file = self.get(file=file_path)
                file.name = re.sub(r'[^a-z0-9._]+', '_', file.name.lower())
                file.owner = user
                file.owner_username = user.username
                file.update_dt = datetime.now()
            except:
                file = self.model(**{
                    'file':file_path,
                    'name':file.name,
                    'content_type':ContentType.objects.get_for_model(instance),
                    'object_id':instance_pk,
                    'creator':user,
                    'creator_username':user.username,
                    'owner':user,
                    'owner_username':user.username,
                })

            file.save() # auto generate GUID if missing
            files_saved.append(file)

        return files_saved

    def save_files_for_instance(self, request, instance, **kwargs):
        """
        Save files and associate with instance.
        Return list of files saved.
        """

        files = request.FILES.values()
        if 'files' in kwargs:  # 'files' key overwrites request
            files = kwargs.get('files') or []

        # loop; save file; save file record in db
        # ----------------------------------------
        files_saved = []
        for file in files:

            # what to save; where to save it
            file.file.seek(0)
            file_path = save_to_disk(file, instance)

            # update file record; or create new file record
            # ----------------------------------------------
            instance_pk = None
            if isinstance(instance.pk, long) or isinstance(instance.pk, int):
                instance_pk = instance.pk

            try:
                file = self.get(file=file_path)
                file.name = re.sub(r'[^a-zA-Z0-9._-]+', '_', file.name)
                file.owner = request.user
                file.owner_username = request.user.username
                file.update_dt = datetime.now()
                file.content_type = ContentType.objects.get_for_model(instance)
                file.object_id = instance_pk
            except:
                file = self.model(**{
                    'file': file_path,
                    'name': file.name,
                    'content_type': ContentType.objects.get_for_model(instance),
                    'object_id': instance_pk,
                    'creator': request.user,
                    'creator_username': request.user.username,
                    'owner': request.user,
                    'owner_username': request.user.username,
                })

            file.save()  # auto generate GUID if missing
            files_saved.append(file)

        return files_saved
