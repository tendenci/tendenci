from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from tendenci.core.registry import site
from tendenci.core.registry.base import CoreRegistry, lazy_reverse
from tendenci.addons.resumes.models import Resume

class ResumeRegistry(CoreRegistry):
    version = '1.0'
    author = _('Schipul - The Web Marketing Company')
    author_email = 'programmers@schipul.com'
    description = _('Users can upload resumes to help with their careers')
    icon = '%simages/icons/resumes-color-64x64.png' % settings.STATIC_URL

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
