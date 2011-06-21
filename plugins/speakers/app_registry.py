from registry import site
from registry.base import PluginRegistry

from models import Speaker


class SpeakerRegistry(PluginRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create speaker biographies easily with photo,' \
                  ' position, tagline and more ..'

site.register(Speaker, SpeakerRegistry)
