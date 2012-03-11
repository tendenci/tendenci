from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import Resume


class ResumeRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Users can upload resumes to help with their careers'
    icon = '/site_media/static/images/icons/resumes-color-64x64.png'
    
    event_logs = {
        'resume':{
            'base':('350000','0099CC'),
            'add':('351000','0099CC'),
            'edit':('352000','0099CC'),
            'delete':('353000','0099CC'),
            'search':('354000','0099CC'),
            'view':('355000','0099CC'),
            'print_view':('355001', '0099CC'),
        }
    }
    
    url = {
        'add': lazy_reverse('resume.add'),
        'search': lazy_reverse('resumes'),
    }

site.register(Resume, ResumeRegistry)
