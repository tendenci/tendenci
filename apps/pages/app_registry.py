from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import Page


class PageRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create pages to display basic content throughout the site'

    url = {
        'add': lazy_reverse('page.add'),
        'search': lazy_reverse('page.search'),
    }

site.register(Page, PageRegistry)
