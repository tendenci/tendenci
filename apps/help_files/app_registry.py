from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import HelpFile


class HelpFileRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create help files, tutorials and more!'
    
    event_logs = {
        'help_file':{
            'base':('1000000','D11300'),
            'add':('1000100','D52500'),
            'edit':('1000200','DA3800'),
            'delete':('1000300','DF4A00'),
            'search':('1000400','E35D00'),
            'view':('1000500','E86F00'),
        },
        'help_file_topic':{
            'base':('1001000','A20900'),
            'add':('1001100','AC1300'),
            'edit':('1001200','B51C00'),
            'delete':('1001300','B51C00'),
            'search':('1001400','C72E00'),
            'view':('1001500','D13800'),
        }
    }

    url = {
        'search': lazy_reverse('help_files.search'),
        'add': lazy_reverse('admin:help_files_helpfile_add'),
        'list': lazy_reverse('help_files'),
    }

site.register(HelpFile, HelpFileRegistry)
