from storages.backends.s3boto import S3BotoStorage
from django.conf import settings

from s3_folder_storage.s3 import DefaultStorage, StaticStorage

class ThemeStorage(S3BotoStorage):
    """
    Storage for uploaded theme files.
    The folder is defined in settings.THEME_S3_PATH
    """

    def __init__(self, *args, **kwargs):
        kwargs['location'] = settings.THEME_S3_PATH
        super(DefaultStorage, self).__init__(*args, **kwargs)