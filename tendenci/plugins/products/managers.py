from django.contrib.auth.models import User
from django.core.files import File as DjangoFile
from perms.managers import TendenciBaseManager
from files.managers import FileManager
from files.managers import save_to_disk


class ProductManager(TendenciBaseManager):
    """
    Model Manager
    """
    pass


class ProductFileManager(FileManager):
    """
    Tools for managing product files
    """

    def bind_files_to_instance(self, files, instance, **kwargs):
        """
        Save files and associate with instance.
        Return list of files saved.
        """
        try:  # explicit user or default to admin
            user = kwargs.get('user') or User.objects.get(id=1)
        except User.DoesNotExist as e:
            return [] # return empty list

        # loop; save file; save file record in db
        # ----------------------------------------

        files_saved = []
        for file in files:

            # what to save; where to save it
            file_path = save_to_disk(file, instance)

            # update file record; or create new file record
            # ----------------------------------------------

            try:
                # get tendenci file object
                file = self.get(file=file_path)
                file.name = file.name
                file.owner = user
                file.owner_username = user.username
                file.update_dt = datetime.now()
            except:
                # make tendenci file object
                file = self.model(**{
                    'product': instance,
                    'file':file_path,
                    'name':file.name,
                    'content_type':ContentType.objects.get_for_model(instance),
                    'object_id':instance.pk,
                    'creator':user,
                    'creator_username':user.username,
                    'owner':user,
                    'owner_username':user.username,
                })

            file.save() # auto generate GUID if missing
            files_saved.append(file)

        return files_saved



