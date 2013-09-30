from django.template import Library
register = Library()


@register.filter
def file_exists(obj):
    """
    Returns boolean
    Checks if file exists at a disk level
    Accepts File, FileField and String [path] type object
    """
    from django.forms import FileField
    from django.core.files.storage import default_storage
    from tendenci.core.files.models import File

    if isinstance(obj, File):
        return default_storage.exists(obj.file.path)

    if isinstance(obj, FileField):
        return default_storage.exists(obj.path)

    if isinstance(obj, basestring) and obj:
        return default_storage.exists(obj)

    return False