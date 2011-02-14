from registry import site
from registry.base import PluginRegistry

from models import Staff


class StaffRegistry(PluginRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create staff biographies easily with photo,' \
                  ' position, tagline and more ..'

site.register(Staff, StaffRegistry)
