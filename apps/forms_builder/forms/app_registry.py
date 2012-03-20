from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import Form


class FormRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create custom forms to take information ' \
                  'throughout the site'
    icon = '/site_media/static/images/icons/cms-forms-color-64x64.png'
    
    event_logs = {
        'form':{
            'base':('587000','33FFFF'),
            'add':('587100','33FFE6'),
            'edit':('587200','33FFCC'),
            'delete':('587300','33FFB3'),
            'search':('587400','33FF99'),
            'view':('587500','33FF80'),
            'export':('587600','33FF33'),
        }
    }

    url = {
        'add': lazy_reverse('form_add'),
        'search': lazy_reverse('forms'),
        'list': lazy_reverse('forms'),
    }

site.register(Form, FormRegistry)
