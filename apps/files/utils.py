import Image
from cStringIO import StringIO
from django.core.cache import cache

def get_image(file, size):
    """
    Gets resized-image-object from cache or rebuilds
    the resized-image-object using the original image-file.
    """

    size = validate_image_size(size)

    str_size = 'x'.join([str(i) for i in size])
    key = '.'.join((file.update_dt.isoformat('.'), str_size))
    # e.g. 2005-08-08.16:09:43.200x300 <date>.<time>.<width>x<height>

    data = cache.get(key)
    if not data: data = build_image(file, size)

    return Image.open(StringIO(data))

def build_image(file, size):
    """
    Builds a resized image based off of the original image.
    """

    image = Image.open(file.file.path) # get image
    image = image.resize(size, Image.ANTIALIAS) # resize image

    output = StringIO()
    image.save(output, "JPEG", quality=100)
    data = output.getvalue()
    output.close()

    str_size = 'x'.join([str(i) for i in size])
    key = '.'.join((file.update_dt.isoformat('.'), str_size))
    # e.g. 2005-08-08.16:09:43.200x300 <date>.<time>.<width>x<height>

    cache.add(key, data, 60*60*24*365) # cache for 1 year
    
    return data

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
