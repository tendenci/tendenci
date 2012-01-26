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
    
    event_logs = {
        'story':{
            'base':('1060000','FF33FF'),
            'add':('1060100','FF33FF'),
            'edit':('1060200','DD77AA'),
            'delete':('1060300','CC9980'),
            'search':('1060400','AADD2B'),
            'view':('1060500','99FF00'),
            'print_view':('1060501', '99FF00'),
        },
    }
    
    url = {
        'add': lazy_reverse('story.add'),
        'search': lazy_reverse('story.search'),
    }

site.register(Story, StoryRegistry)
