#### utils.py

import os
import Image
import urllib2
from os.path import exists
from cStringIO import StringIO
from django.conf import settings
from django.shortcuts import Http404
from django.core.cache import cache as django_cache
from tendenci.core.base.utils import image_rescale


def get_image(file, size, pre_key, crop=False, quality=90, cache=False, unique_key=None):
    """
    Gets resized-image-object from cache or rebuilds
    the resized-image-object using the original image-file.
    *pre_key is either:
        from tendenci.addons.photos.cache import PHOTO_PRE_KEY
        from tendenci.core.files.cache import FILE_IMAGE_PRE_KEY
    """

    size = validate_image_size(size)  # make sure it's not too big
    binary = None

    # if cache:
    #     key = generate_image_cache_key(file, size, pre_key, crop, unique_key)
    #     binary = django_cache.get(key)  # check if key exists

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

    if settings.USE_S3_STORAGE:
        file_path = os.path.join(settings.MEDIA_URL, unicode(file))
        response = urllib2.urlopen(file_path)  # can raise 404
        image = Image.open(StringIO(response.read()))
    else:
        if hasattr(file, 'path') and exists(file.path):
            image = Image.open(file.path)  # get image
        else:
            raise Http404

    # handle infamous error
    # IOError: cannot write mode P as JPEG
    if image.mode != "RGB":
        image = image.convert("RGB")

    if crop:
        image = image_rescale(image, size)  # thumbnail image
    else:
        image = image.resize(size, Image.ANTIALIAS)  # resize image

    # mission: get binary
    output = StringIO()
    image.save(output, "JPEG", quality=quality)
    binary = output.getvalue()  # mission accomplished
    output.close()

    if cache:
        key = generate_image_cache_key(file, size, pre_key, crop, unique_key)
        django_cache.add(key, binary, 60 * 60 * 24 * 30)  # cache for 30 days #issue/134

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
        if item[0] > item[1]:
            new_size.append(item[1])
        else:
            new_size.append(item[0])

    return new_size


def aspect_ratio(image_size, new_size, constrain=False):
    """
    The image_size is a sequence of integers (200, 300)
    The new_size is a sequence of integers (200, 300)
    The constrain limits to within the new_size parameters.
    """

    w, h = new_size

    if not constrain and (w and h):
        return w, h

    if bool(w) != bool(h):
        if w:
            return constrain_size(image_size, [w, 0])
        return constrain_size(image_size, [0, h])

    if not constrain:
        if bool(w) != bool(h):
            return constrain_size(image_size, [w, 0])

    w1, h1 = constrain_size(image_size, [w, 0])
    w2, h2 = constrain_size(image_size, [0, h])

    if h1 <= h:
        return w1, h1

    return w2, h2


def constrain_size(image_size, new_size):
    """
    Take the biggest integer in the 2-item sequence
    and constrain on that integer.
    """

    w, h = new_size
    max_size = max(new_size)

    ow, oh = image_size  # original width and height
    ow = float(ow)

    if w == max_size:
        h = (oh / ow) * w
    else:  # height is max size
        w = h / (oh / ow)

    return int(w), int(h)


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
        key = '.'.join((settings.CACHE_PRE_KEY, pre_key, str(file.size), file.name, str_size, str_crop))
    # Remove spaces so key is valid for memcached
    key = key.replace(" ", "_")

    return key
