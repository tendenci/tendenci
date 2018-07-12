from django.utils.translation import ugettext_lazy as _

from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import CoreRegistry, lazy_reverse
from tendenci.apps.redirects.models import Redirect
from tendenci.apps.theme.templatetags.static import static


class RedirectRegistry(CoreRegistry):
    version = '1.0'
    author = _('Tendenci - The Open Source AMS for Associations')
    author_email = 'programmers@tendenci.com'
    description = _('Add redirects to preserve SEO')
    icon = static('images/icons/redirects-color-64x64.png')

    url = {
        'add': lazy_reverse('redirect.add'),
        'search': lazy_reverse('redirects'),
    }

site.register(Redirect, RedirectRegistry)
