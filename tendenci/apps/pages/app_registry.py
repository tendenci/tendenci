from django.utils.translation import ugettext_lazy as _

from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import CoreRegistry, lazy_reverse
from tendenci.apps.pages.models import Page
from tendenci.apps.theme.templatetags.static import static


class PageRegistry(CoreRegistry):
    version = '1.0'
    author = _('Tendenci - The Open Source AMS for Associations')
    author_email = 'programmers@tendenci.com'
    description = _('Create pages to display basic content throughout the site')
    icon = static('images/icons/pages-color-64x64.png')

    event_logs = {
        'page':{
            'base':('580000','009900'),
            'add':('581000','009933'),
            'edit':('582000','009966'),
            'delete':('583000','00CC00'),
            'search':('584000','00FF00'),
            'view':('585000','00FF33'),
            'print_view':('585001','00FF33')
        }
    }
    url = {
        'add': lazy_reverse('page.add'),
        'search': lazy_reverse('page.search'),
    }

site.register(Page, PageRegistry)
