from registry import site
from registry.base import PluginRegistry, lazy_reverse
from models import Attorney


class AttorneyRegistry(PluginRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Attorneys plugin for showing a list of Attorneys.'

site.register(Attorney, AttorneyRegistry)
