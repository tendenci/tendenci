from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import Job


class JobRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create job listings for hiring'

    url = {
        'add': lazy_reverse('job.add'),
        'search': lazy_reverse('job.search'),
    }

site.register(Job, JobRegistry)
