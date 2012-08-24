from tendenci.core.registry import site
from tendenci.core.registry.base import AppRegistry, lazy_reverse
from tendenci.addons.culintro.models import CulintroJob


class CulintroJobRegistry(AppRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create projects type of content'

    url = {
        'add': lazy_reverse('culintro.add'),
        'search': lazy_reverse('culintro.search'),
    }

site.register(CulintroJob, CulintroJobRegistry)
