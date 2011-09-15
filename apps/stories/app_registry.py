from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import Story


class StoryRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Stories can be created and rotated on ' \
                  'a specified area on the site'
    icon = '/site_media/static/images/icons/stories-color-64x64.png'

    url = {
        'add': lazy_reverse('story.add'),
        'search': lazy_reverse('story.search'),
    }

site.register(Story, StoryRegistry)
