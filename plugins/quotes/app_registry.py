from registry import site
from registry.base import PluginRegistry, lazy_reverse
from models import Quote


class QuoteRegistry(PluginRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create quotes that can be rotated or listed on the site'

site.register(Quote, QuoteRegistry)
