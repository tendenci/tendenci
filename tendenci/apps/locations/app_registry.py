from django.utils.translation import ugettext_lazy as _

from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import CoreRegistry, lazy_reverse
from tendenci.apps.locations.models import Location
from tendenci.apps.theme.templatetags.static import static


class LocationRegistry(CoreRegistry):
    version = '1.0'
    author = _('Tendenci - The Open Source AMS for Associations')
    author_email = 'programmers@tendenci.com'
    description = _('A list of locations associated with your organization'
        'Includes a search that sort by nearest location.')
    icon = static('images/icons/locations-color-64x64.png')

    event_logs = {
        'location':{
            'base':('830000', '669933'),
            'add':('831000', '669966'),
            'edit':('832000', '66CC66'),
            'delete':('833000', '66CC00'),
            'search':('834000', '66CC33'),
            'view':('835000', '66CC99'),
        }
    }

    url = {
        'add': lazy_reverse('location.add'),
        'search': lazy_reverse('location.search'),
        'list': lazy_reverse('locations'),
    }

site.register(Location, LocationRegistry)
