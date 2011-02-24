from django.contrib.contenttypes.models import ContentType
from django.db.models import Manager
from haystack.query import SearchQuerySet
import re

def save_to_disk(f, instance):
    import os
    from settings import MEDIA_ROOT

    file_name = re.sub(r'[^a-zA-Z0-9._]+', '-', f.name)

    relative_directory = os.path.join(
        'files',
        instance._meta.app_label,
        instance._meta.module_name,
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

class FileManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
            Uses Haystack to query. 
            Returns a SearchQuerySet
        """
        sqs = SearchQuerySet()
        
        if query: 
            sqs = sqs.auto_query(sqs.query.clean(query))
        else:
            sqs = sqs.all()

        sqs = sqs.order_by('-update_dt')
        
        return sqs.models(self.model)

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
                    'object_id':instance.pk,
                    'creator':request.user,
                    'creator_username':request.user.username,
                    'owner':request.user,
                    'owner_username':request.user.username,
                })

            file.save() # auto generate GUID if missing
            files_saved.append(file)

        return files_saved