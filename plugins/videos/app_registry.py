from registry import site
from registry.base import PluginRegistry, lazy_reverse
from models import Video


class VideoRegistry(PluginRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Add video and display them in a grid format'
    
    event_logs = {
        'video':{
            'base':('1200000','993355'),
            'add':('1200100','119933'),
            'edit':('1200200','EEDD55'),
            'delete':('1200300','AA2222'),
            'search':('1200400','CC55EE'),
            'view':('1200500','55AACC'),
        }
    }

site.register(Video, VideoRegistry)
