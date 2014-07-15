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


def get_file_content(name, storage_type='default'):
    """
    Get the file content from the specified storage.
    """
    if storage_type == 'static':
        storage = get_static_storage()
    else:
        storage = get_default_storage()
    f = storage.open(name)
    content = f.read()
    f.close()

    return content

def save_file_content(name, content, storage_type='default'):
    """
    Save the file content to the specified storage.
    """
    if storage_type == 'static':
        storage = get_static_storage()
    else:
        storage = get_default_storage()

    return storage.save(name, content)

