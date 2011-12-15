from registry import site
from registry.base import PluginRegistry, lazy_reverse
from museums.models import Museum


class MuseumRegistry(PluginRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create museums type of content'

site.register(Museum, MuseumRegistry)
