from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import Form


class FormRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create custom forms to take information ' \
                  'throughout the site'

    url = {
        'add': lazy_reverse('form_add'),
        'search': lazy_reverse('forms'),
    }

site.register(Form, FormRegistry)
