from django.conf import settings
from django.core.files.storage import get_storage_class

def get_default_storage():
    """
    Get a default storage class.
    """
    return get_storage_class(settings.DEFAULT_FILE_STORAGE)()

def get_static_storage():
    """
    Get a static storage class.
    """
    return get_storage_class(settings.STATICFILES_STORAGE)()
