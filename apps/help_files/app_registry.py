from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import HelpFile


class HelpFileRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create help files, tutorials and more!'

site.register(HelpFile, HelpFileRegistry)
