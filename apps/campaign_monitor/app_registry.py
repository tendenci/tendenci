from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import Template


class TemplateRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create templates via the Campaign Monitor API'

    url = {
        'add': lazy_reverse('campaign_monitor.template_add'),
        'search': lazy_reverse('campaign_monitor.template_index'),
    }

site.register(Template, TemplateRegistry)
