from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import CoreRegistry, lazy_reverse
from tendenci.apps.navs.models import Nav
from django.utils.translation import ugettext_lazy as _


class NavRegistry(CoreRegistry):
    version = '1.0'
    author = _('Tendenci - The Open Source AMS for Associations')
    author_email = 'programmers@tendenci.com'
    description = _('Create navs for navigation')

    url = {
        'add': lazy_reverse('navs.add'),
        'search': lazy_reverse('navs.search'),
    }

site.register(Nav, NavRegistry)
