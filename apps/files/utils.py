import Image
from cStringIO import StringIO
from django.core.cache import cache

from files.cache import FILE_IMAGE_PRE_KEY

def get_image(file, size):
    """
    Gets resized-image-object from cache or rebuilds
    the resized-image-object using the original image-file.
    """
    size = validate_image_size(size) # make sure it's not too big
    key = generate_image_cache_key(file, size)

    binary = cache.get(key)
    if not binary: binary = build_image(file, size)

    try: return Image.open(StringIO(binary))
    except: return ''

def build_image(file, size):
    """
    Builds a resized image based off of the original image.
    """
    image = Image.open(file.file.path) # get image
    image = image.resize(size, Image.ANTIALIAS) # resize image

    # mission: get binary
    output = StringIO()
    image.save(output, "JPEG", quality=100)
    binary = output.getvalue() # mission accomplished
    output.close()

    key = generate_image_cache_key(file, size)

    cache.add(key, binary, 60*60*24*30) # cache for 30 days #issue/134
    
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

def generate_image_cache_key(file, size):
    """
    Generates image cache key. You can use this for adding, 
    retrieving or removing a cache record.
    """
    str_size = 'x'.join([str(i) for i in size])
    key = '.'.join((FILE_IMAGE_PRE_KEY, file.update_dt.isoformat('.'), str_size))
    # e.g. file_image.2005-08-08.16:09:43.200x300 file_image.<date>.<time>.<width>x<height>
    
    return key


