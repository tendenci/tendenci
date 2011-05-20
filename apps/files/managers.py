import os
import re
from django.contrib.contenttypes.models import ContentType
from django.db.models import Manager
from haystack.query import SearchQuerySet
from perms.managers import TendenciBaseManager
from settings import MEDIA_ROOT

def save_to_disk(f, instance):
    """
    Takes file object and instance (or model).
    Returns back relative path of file.
    """

    file_name = re.sub(r'[^a-zA-Z0-9._]+', '-', f.name)

    # make dir with app and module name
    relative_directory = os.path.join(
        'files',
        instance._meta.app_label,
        instance._meta.module_name,
    )

    # make directory w/ pk
    if isinstance(instance.pk, long):
        relative_directory = os.path.join(
            relative_directory, 
            unicode(instance.pk),
        )

    absolute_directory = os.path.join(MEDIA_ROOT, relative_directory)

    if not os.path.exists(absolute_directory):
        os.makedirs(absolute_directory)

    destination = open(os.path.join(absolute_directory, file_name), 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()

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

    def save_files_for_instance(self, request, instance, **kwargs):
        """
        Save files and associate with instance.
        Return list of files saved.
        """

        if not len(request.FILES) and not kwargs.get('files'):
            return []

        files = kwargs.get('files') or request.FILES.values()

        # loop; save file; save file record in db
        # ----------------------------------------

        files_saved = []
        for file in files:

            file_path = save_to_disk(file, instance)

            # update file record; or create new file record
            # ----------------------------------------------

            instance_pk = None
            if isinstance(instance.pk, long):
                instance_pk = instance.pk

            try:
                file = self.get(file=file_path)
                file.name = file.name
                file.owner = request.user
                file.owner_username = request.user.username
            except:
                file = self.model(**{
                    'file':file_path,
                    'name':file.name,
                    'content_type':ContentType.objects.get_for_model(instance),
                    'object_id':instance_pk,
                    'creator':request.user,
                    'creator_username':request.user.username,
                    'owner':request.user,
                    'owner_username':request.user.username,
                })

            file.save() # auto generate GUID if missing
            files_saved.append(file)

        return files_saved