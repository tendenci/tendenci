from tendenci.core.registry import site
from tendenci.core.registry.base import AppRegistry, lazy_reverse
from tendenci.apps.services.models import Service


class ServiceRegistry(AppRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create services that can be offered to people'

    url = {
        'add': lazy_reverse('service.add'),
        'search': lazy_reverse('services'),
        'list': lazy_reverse('services'),
    }

site.register(Service, ServiceRegistry)
