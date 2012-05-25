from registry import site
from registry.base import PluginRegistry, lazy_reverse
from models import Service


class ServiceRegistry(PluginRegistry):
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
