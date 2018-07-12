from django.utils.translation import ugettext_lazy as _

from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import CoreRegistry, lazy_reverse
from tendenci.apps.resumes.models import Resume
from tendenci.apps.theme.templatetags.static import static

class ResumeRegistry(CoreRegistry):
    version = '1.0'
    author = _('Tendenci - The Open Source AMS for Associations')
    author_email = 'programmers@tendenci.com'
    description = _('Users can upload resumes to help with their careers')
    icon = static('images/icons/resumes-color-64x64.png')

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
