from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import Event


class EventRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create directories to list businesses'
    icon = '/site_media/static/images/icons/events-color-64x64.png'
    
    # events
    event_logs = {
        'event':{
            'base':('170000','FF6600'),
            'add':('171000','FF6600'),
            'edit':('172000','FFCC66'),
            'delete':('173000','FF9900'),
            'search':('174000','FF9933'),
            'view':('175000','FF9966'),
        },
        'event_type':{
            'base':('270000','FFCC99'),
            'add':('271000','FFCC99'),
            'edit':('272000','FFCC99'),
            'delete':('273000','FFCC99'),
            'search':('274000','FFCC99'),
            'view':('275000','FFCC99'),
        }
    }
    
    url = {
        'add': lazy_reverse('event.add'),
        'search': lazy_reverse('event.search'),
        'list': lazy_reverse('events'),
    }

site.register(Event, EventRegistry)
