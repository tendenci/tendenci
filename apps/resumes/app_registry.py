from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import Resume


class ResumeRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Users can upload resumes to help with their careers'

    url = {
        'add': lazy_reverse('resume.add'),
        'search': lazy_reverse('resume.search'),
    }

site.register(Resume, ResumeRegistry)
