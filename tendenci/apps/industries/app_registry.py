from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import CoreRegistry
from tendenci.apps.industries.models import Industry


class IndustryRegistry(CoreRegistry):
    version = '1.0'
    author = 'Tendenci - The Open Source AMS for Associations'
    author_email = 'programmers@tendenci.com'
    description = 'A list of industries'
    #icon = static('images/icons/industries-color-64x64.png')

    event_logs = {
        'industry': {
            'base': ('930000', '003399'),
            'add': ('931000', '003366'),
            'edit': ('932000', '003333'),
            'delete': ('933000', '003300'),
            'search': ('934000', '0033cc'),
            'view': ('935000', '0033ee'),
        }
    }

#    url = {
#        'add': lazy_reverse('industry.add'),
#        'search': lazy_reverse('industry.search'),
#        'list': lazy_reverse('industries'),
#    }

site.register(Industry, IndustryRegistry)
