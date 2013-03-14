from tendenci.core.registry import site
from tendenci.core.registry.base import CoreRegistry, lazy_reverse
from tendenci.addons.industries.models import Industry


class IndustryRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'A list of industries'
    #icon = '%simages/icons/industries-color-64x64.png' % settings.STATIC_URL

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
