from registry import site
from registry.base import PluginRegistry, lazy_reverse
from models import BeforeAndAfter


class BeforeAndAfterRegistry(PluginRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Before and After Gallery for showcasing different items.'
    
    event_logs = {
        'before_and_after':{
            'base':('1090000','FFCCBB'),
            'add':('1090100','119933'),
            'edit':('1090200','EEDD55'),
            'delete':('1090300','AA2222'),
            'search':('1090400','CC55EE'),
            'view':('1090500','55AACC'),
        }
    }

site.register(BeforeAndAfter, BeforeAndAfterRegistry)
