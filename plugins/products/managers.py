from django.core.files import File as DjangoFile
from perms.managers import TendenciBaseManager
from files.managers import FileManager


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
        super(ProductFileManager, self).bind_files_to_instance(files, instance, **kwargs)

        for file in files:
            django_file = DjangoFile(file)
            self.create(**{
                'file':django_file,
                'product':instance,
            })