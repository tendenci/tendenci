from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import CoreRegistry
from tendenci.apps.boxes.models import Box
from django.utils.translation import ugettext_lazy as _


class BoxRegistry(CoreRegistry):
    version = '1.0'
    author = _('Tendenci - The Open Source AMS for Associations')
    author_email = 'programmers@tendenci.com'
    description = _('Create boxes that allow editable areas in the site theme')

    event_logs = {
        'box':{
            'base':('1100000','5588AA'),
            'add':('1100100','119933'),
            'edit':('1100200','EEDD55'),
            'delete':('1100300','AA2222'),
        }
    }

site.register(Box, BoxRegistry)
