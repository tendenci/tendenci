from registry import site
from registry.base import PluginRegistry, lazy_reverse
from models import BeforeAndAfter


class BeforeAndAfterRegistry(PluginRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Before and After Gallery for showcasing different items.'

site.register(BeforeAndAfter, BeforeAndAfterRegistry)
