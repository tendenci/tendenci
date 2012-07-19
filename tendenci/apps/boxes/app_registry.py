from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import Box


class BoxRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create boxes that allow editable areas in the site theme'
    
    event_logs = {
        'box':{
            'base':('1100000','5588AA'),
            'add':('1100100','119933'),
            'edit':('1100200','EEDD55'),
            'delete':('1100300','AA2222'),
        }
    }

site.register(Box, BoxRegistry)
