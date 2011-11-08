from registry import site
from registry.base import PluginRegistry, lazy_reverse
from plugs.models import Plug


class PlugRegistry(PluginRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create plugs type of content'

site.register(Plug, PlugRegistry)
