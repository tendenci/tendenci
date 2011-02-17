from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import Box


class BoxRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create boxes that allow editable areas in the site theme'

site.register(Box, BoxRegistry)
