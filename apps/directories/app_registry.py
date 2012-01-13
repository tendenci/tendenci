from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import Directory


class DirectoryRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create directories to list businesses'
    icon = '/site_media/static/images/icons/directories-color-64x64.png'
    
    event_logs = {
        'directory':{
            'base':('440000','CCCC33'),
            'add':('441000','CCCC33'),
            'edit':('442000','CCCC33'),
            'delete':('443000','CCCC33'),
            'search':('444000','CCCC33'),
            'view':('445000','CCCC33'),
            'print_view':('445001','CCCC33'),
            'renew':('442210','CCCC33'),
        }
    }

    url = {
        'add': lazy_reverse('directory.add'),
        'search': lazy_reverse('directory.search'),
    }

site.register(Directory, DirectoryRegistry)
