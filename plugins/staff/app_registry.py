from registry import site
from registry.base import PluginRegistry

from models import Staff


class StaffRegistry(PluginRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create staff biographies easily with photo,' \
                  ' position, tagline and more ..'
                  
    event_logs = {
        'staff':{
            'base':('1080000','EE7733'),
            'add':('1080100','119933'),
            'edit':('1080200','EEDD55'),
            'delete':('1080300','AA2222'),
            'search':('1080400','CC55EE'),
            'view':('1080500','55AACC'),
        }
    }

site.register(Staff, StaffRegistry)
