from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import Directory


class DirectoryRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create directories to list businesses'
    icon = '/site_media/static/images/icons/directories-color-64x64.png'

    url = {
        'add': lazy_reverse('directory.add'),
        'search': lazy_reverse('directory.search'),
    }

site.register(Directory, DirectoryRegistry)
