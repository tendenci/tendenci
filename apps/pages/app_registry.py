from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import Page


class PageRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create pages to display basic content throughout the site'
    icon = '/site_media/static/images/icons/pages-color-64x64.png'
    
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
