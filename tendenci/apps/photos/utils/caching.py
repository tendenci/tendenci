from builtins import str

from django.http import HttpResponse
from django.conf import settings
from django.core.cache import cache
from django.urls import reverse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from tendenci.apps.files.utils import get_image, aspect_ratio, generate_image_cache_key

from tendenci.apps.photos.cache import PHOTO_PRE_KEY
from tendenci.apps.photos.models import Image


def cache_photo_size(id, size, crop=False, quality=90, download=False, constrain=False):
    """
    """
    if isinstance(quality, str) and quality.isdigit():
        quality = int(quality)

    cache_key = generate_image_cache_key(file=str(id), size=size, pre_key=PHOTO_PRE_KEY, crop=crop, unique_key=str(id), quality=quality, constrain=constrain)
    cached_image = cache.get(cache_key)
    if cached_image:
        return cached_image

    try:
        photo = Image.objects.get(id=id)
    except:
        return ""

    args = [id, size]
    if crop:
        args.append("crop")
    if constrain:
        args.append("constrain")
    if quality:
        args.append(quality)
    request_path = reverse('photo.size', args=args)

    size = [int(s) for s in size.split('x')]
    size = aspect_ratio(photo.image_dimensions(), size, constrain)

    # gets resized image from cache or rebuild
    image = get_image(photo.image, size, PHOTO_PRE_KEY, crop=crop, quality=quality, unique_key=str(photo.pk), constrain=constrain)

    # if image not rendered; quit
    if not image:
        return request_path
    
    if image.mode in ("RGBA", "P"):
        image = image.convert('RGB')

    response = HttpResponse(content_type='image/jpeg')
    response['Content-Disposition'] = ' filename="%s"' % photo.image_filename()
    image.save(response, "JPEG", quality=quality)

    if photo.is_public_photo() and photo.is_public_photoset():
        file_name = photo.image_filename()
        file_path = 'cached%s%s' % (request_path, file_name)
        default_storage.save(file_path, ContentFile(response.content))
        full_file_path = "%s%s" % (settings.MEDIA_URL, file_path)
        cache.set(cache_key, full_file_path)
        cache_group_key = "photos_cache_set.%s" % photo.pk
        cache_group_list = cache.get(cache_group_key)

        if cache_group_list is None:
            cache.set(cache_group_key, [cache_key])
        else:
            cache_group_list += [cache_key]
            cache.set(cache_group_key, cache_group_list)

        return full_file_path
    return request_path
