from registry import site
from site_settings.utils import get_setting
from registry.base import PluginRegistry, lazy_reverse
from models import Job


class JobRegistry(PluginRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create %s listings for hiring' %  get_setting('module', 'jobs', 'label')
    icon = '/site_media/static/images/icons/jobs-color-64x64.png'
    
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
        'search': lazy_reverse('job.search'),
        'list': lazy_reverse('jobs')
    }

site.register(Job, JobRegistry)
