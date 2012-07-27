from tendenci.core.registry import site
from tendenci.core.registry.base import AppRegistry, lazy_reverse
from tendenci.apps.architecture_projects.models import ArchitectureProject


class ArchitectureProjectRegistry(AppRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create architecture projects of clients'
    
    event_logs = {
        'architecture_project':{
            'base':('1000000','EE8877'),
            'add':('1000100','119933'),
            'edit':('1000200','EEDD55'),
            'delete':('1000300','AA2222'),
            'search':('1000400','CC55EE'),
            'view':('1000500','55AACC'),
        }
    }

site.register(ArchitectureProject, ArchitectureProjectRegistry)
