from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import Location


class LocationRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'A list of locations associated with your organization' \
        'Includes a search that sort by nearest location.'
    icon = '/site_media/static/images/icons/locations-color-64x64.png'

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
