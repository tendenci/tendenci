from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import PhotoSet


class PhotoSetRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Upload photos for the world to see!'
    icon = '/site_media/static/images/icons/photo-albums-color-64x64.png'

    url = {
        'add': lazy_reverse('photoset_add'),
        'search': lazy_reverse('photoset_latest'),
    }

site.register(PhotoSet, PhotoSetRegistry)
