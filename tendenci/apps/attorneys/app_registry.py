from tendenci.core.registry import site
from tendenci.core.registry.base import AppRegistry, lazy_reverse
from tendenci.apps.attorneys.models import Attorney


class AttorneyRegistry(AppRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Attorneys plugin for showing a list of Attorneys.'
    
    event_logs = {
        'attorney':{
            'base':('490000','773300'),
            'add':('491000','119933'),
            'edit':('492000','EEDD55'),
            'delete':('493000','AA2222'),
            'search':('494000','CC55EE'),
            'detail':('495000','55AACC'),
            'index':('496000','886655'),
        }
    }

site.register(Attorney, AttorneyRegistry)
