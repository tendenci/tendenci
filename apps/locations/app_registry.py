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

    url = {
        'add': lazy_reverse('location.add'),
        'search': lazy_reverse('location.search'),
    }

site.register(Location, LocationRegistry)
