from registry import site
from registry.base import PluginRegistry, lazy_reverse
from lots.models import Lot


class LotRegistry(PluginRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create lots type of content'

    url = {
        'add': lazy_reverse('lots.map_add'),
        'search': lazy_reverse('lots'),
        'list': lazy_reverse('lots'),
    }

site.register(Lot, LotRegistry)
