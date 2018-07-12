from django.utils.translation import ugettext_lazy as _

from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import CoreRegistry
from tendenci.apps.regions.models import Region


class RegionRegistry(CoreRegistry):
    version = '1.0'
    author = _('Tendenci - The Open Source AMS for Associations')
    author_email = 'programmers@tendenci.com'
    description = _('A list of regions')
    #icon = static('images/icons/regions-color-64x64.png')

    event_logs = {
        'regions': {
            'base': ('930000', '006699'),
            'add': ('931000', '006666'),
            'edit': ('932000', '006633'),
            'delete': ('933000', '006600'),
            'search': ('934000', '0066cc'),
            'view': ('935000', '0066ee'),
        }
    }

#    url = {
#        'add': lazy_reverse('industry.add'),
#        'search': lazy_reverse('industry.search'),
#        'list': lazy_reverse('industries'),
#    }

site.register(Region, RegionRegistry)
