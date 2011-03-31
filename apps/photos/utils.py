import Image
from os import stat
from stat import ST_MODE
from os.path import exists
from cStringIO import StringIO
from django.core.cache import cache
from photos.cache import PHOTO_PRE_KEY
from base.utils import image_rescale

def dynamic_image(photo, size, crop):
    """
    Gets resized-image-object from cache or rebuilds
    the resized-image-object using the original image-file.
    """
    # if file does not exist; then quit
    if not exists(photo.image.path): return None

    size = validate_image_size(size) # make sure it's not too big
    key = generate_image_cache_key(photo, size, crop)

    binary = cache.get(key) # check if key exists

    if not binary:
        binary = build_image(photo, size, crop)

    try: return Image.open(StringIO(binary))
    except: return ''

def build_image(photo, size, crop=False):
    """
    Builds a resized image based off of the original image.
    """

    image = Image.open(photo.image.path) # get image
    if image.mode != "RGB":
        image = image.convert("RGB")
    if crop:
        # thumbnail does not return image
        # affects itself; weirdo
        image = image_rescale(image, size)
    else:
        image = image.resize(size, Image.ANTIALIAS) # resize image

    # mission: get binary
    output = StringIO()
    image.save(output, "JPEG", quality=100)
    binary = output.getvalue() # mission accomplished
    output.close()

    key = generate_image_cache_key(photo, size, crop)

    cache.add(key, binary, 60*60*24*30) # cache for 30 days
    
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

def generate_image_cache_key(photo, size, crop=False):
    """
    Generates image cache key. You can use this for adding, 
    retrieving or removing a cache record.
    """

    str_crop = ""
    if crop: str_crop = "cropped" 

    # special method that pulls "last modification"
    last_modification = stat(photo.image.path)[ST_MODE]

    str_size = 'x'.join([str(i) for i in size])
    key = '.'.join((PHOTO_PRE_KEY, str(photo.pk), str(last_modification), str_size, str_crop))
    # e.g. photo.23.33206.200x300.cropped <pre-key>.<pk>.<last_modification>.<width>x<height>.<cropped>

    return key