from registry import site
from registry.base import PluginRegistry, lazy_reverse
from tenents.models import Tenent


class TenentRegistry(PluginRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create tenents type of content'

    url = {
        'add': lazy_reverse('tenents.maps.add'),
        'search': lazy_reverse('tenents.maps'),
        'list': lazy_reverse('tenents.maps'),
    }

site.register(Tenent, TenentRegistry)
