from django.utils.translation import ugettext_lazy as _

from tendenci.apps.registry.sites import site
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.registry.base import CoreRegistry, lazy_reverse
from tendenci.apps.jobs.models import Job
from tendenci.apps.theme.templatetags.static import static


class JobRegistry(CoreRegistry):
    version = '1.0'
    author = _('Tendenci - The Open Source AMS for Associations')
    author_email = 'programmers@tendenci.com'
    description = _('Create and Manage a %(label)s Bank to offer free and paid postings' % {
        'label': get_setting('module', 'jobs', 'label')})
    icon = static('images/icons/jobs-color-64x64.png')

    # jobs - GREEN base - complement is DEEP RED
    event_logs = {
        'job':{
            'base':('250000','669900'),
            'add':('251000','669900'),
            'edit':('252000','666600'),
            'delete':('253000','66FF66'),
            'search':('254000','66FF33'),
            'view':('255000','00CC66'),
            'print_view':('255001','336600'),
        }
    }

    url = {
        'add': lazy_reverse('job.add'),
        'search': lazy_reverse('jobs'),
        'list': lazy_reverse('jobs')
    }

site.register(Job, JobRegistry)
