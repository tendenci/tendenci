import Image
from stat import ST_MODE
from os import stat
from os.path import exists
from cStringIO import StringIO

from django.core.cache import cache as django_cache
from django.conf import settings

from base.utils import image_rescale


def get_image(file, size, pre_key, crop=False, quality=90, cache=False, unique_key=None):
    """
    Gets resized-image-object from cache or rebuilds
    the resized-image-object using the original image-file.
    *pre_key is either:
        from photos.cache import PHOTO_PRE_KEY
        from files.cache import FILE_IMAGE_PRE_KEY
    """
    size = validate_image_size(size) # make sure it's not too big
    binary = None

    if cache:
        key = generate_image_cache_key(file, size, pre_key, crop, unique_key)
        binary = django_cache.get(key) # check if key exists
        
    if not binary:
        kwargs = {
            'crop': crop,
            'cache': cache,
            'quality': quality,
            'unique_key': unique_key,
        }
        binary = build_image(file, size, pre_key, **kwargs)

    try:
        return Image.open(StringIO(binary))
    except:
        return ''


def build_image(file, size, pre_key, crop=False, quality=90, cache=False, unique_key=None):
    """
    Builds a resized image based off of the original image.
    """
    
    try:
        quality = int(quality)
    except:
        quality = 90


    if hasattr(file,'path') and exists(file.path):
        image = Image.open(file.path) # get image
    else:
        return None

    # handle infamous error
    # IOError: cannot write mode P as JPEG
    if image.mode != "RGB":
        image = image.convert("RGB")
    if crop:
        image = image_rescale(image, size) # thumbnail image
    else:
        image = image.resize(size, Image.ANTIALIAS) # resize image

    # mission: get binary
    output = StringIO()
    image.save(output, "JPEG", quality=quality)
    binary = output.getvalue() # mission accomplished
    output.close()

    if cache:
        key = generate_image_cache_key(file, size, pre_key, crop, unique_key)
        django_cache.add(key, binary, 60*60*24*30) # cache for 30 days #issue/134

    return binary


def validate_image_size(size):
    """
    We cap our image sizes to avoid processor overload
    This method checks the size passed and returns
    a valid image size.
    """
    max_size = (2048, 2048)
    new_size = []

    # limit width and height exclusively
    for item in zip(size, max_size):
        if item[0] > item[1]: new_size.append(item[1])
        else: new_size.append(item[0])

    return new_size


def generate_image_cache_key(file, size, pre_key, crop, unique_key):
    """
    Generates image cache key. You can use this for adding,
    retrieving or removing a cache record.
    """
    str_size = 'x'.join([str(i) for i in size])

    if crop: 
        str_crop = "cropped"
    else:
        str_crop = ""

    # e.g. file_image.1294851570.200x300 file_image.<file-system-modified-time>.<width>x<height>
    if unique_key:
        key = '.'.join((settings.CACHE_PRE_KEY, pre_key, unique_key, str_size, str_crop))
    else:
        if hasattr(file,'path'):
            key = '.'.join((settings.CACHE_PRE_KEY, pre_key, str(stat(file.path).st_mtime), file.name, str_size, str_crop))
        else:
            key = '.'.join((settings.CACHE_PRE_KEY, pre_key, str(stat(file.name).st_mtime), file.name, str_size, str_crop))
    # Remove spaces so key is valid for memcached
    key = key.replace(" ","_")

    return key
