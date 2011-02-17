from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import PhotoSet


class PhotoSetRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Upload photos for the world to see!'

    url = {
        'add': lazy_reverse('photoset_add'),
        'search': lazy_reverse('photoset_latest'),
    }

site.register(PhotoSet, PhotoSetRegistry)
