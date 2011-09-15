from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import Redirect


class RedirectRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Add redirects to preserve SEO'
    icon = '/site_media/static/images/icons/redirects-color-64x64.png'

    url = {
        'add': lazy_reverse('redirect.add'),
        'search': lazy_reverse('redirects'),
    }

site.register(Redirect, RedirectRegistry)
