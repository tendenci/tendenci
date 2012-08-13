from django.conf import settings

from tendenci.core.registry import site
from tendenci.core.registry.base import CoreRegistry, lazy_reverse
from tendenci.apps.redirects.models import Redirect


class RedirectRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Add redirects to preserve SEO'
    icon = '%simages/icons/redirects-color-64x64.png' % settings.STATIC_URL

    url = {
        'add': lazy_reverse('redirect.add'),
        'search': lazy_reverse('redirects'),
    }

site.register(Redirect, RedirectRegistry)
