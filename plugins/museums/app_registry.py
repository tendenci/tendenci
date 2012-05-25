from registry import site
from registry.base import PluginRegistry, lazy_reverse
from museums.models import Museum

class MuseumRegistry(PluginRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create museums type of content'
    
    event_logs = {
        'museum':{
            'base':('1440000','773300'),
            'search':('1440400','CC55EE'),
            'detail':('1440500','55AACC'),
        }
    }

site.register(Museum, MuseumRegistry)
