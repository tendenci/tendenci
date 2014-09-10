from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from tendenci.core.registry import site
from tendenci.core.registry.base import CoreRegistry, lazy_reverse
from tendenci.apps.pages.models import Page


class PageRegistry(CoreRegistry):
    version = '1.0'
    author = _('Schipul - The Web Marketing Company')
    author_email = 'programmers@schipul.com'
    description = _('Create pages to display basic content throughout the site')
    icon = '%simages/icons/pages-color-64x64.png' % settings.STATIC_URL

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
