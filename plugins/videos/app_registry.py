from registry import site
from registry.base import PluginRegistry, lazy_reverse
from models import Video


class VideoRegistry(PluginRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Add video and display them in a grid format'

site.register(Video, VideoRegistry)
