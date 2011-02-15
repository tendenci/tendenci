from registry import site
from registry.base import PluginRegistry, lazy_reverse
from models import Donation


class DonationRegistry(PluginRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Allow donations from anyone'

    url = {
        'add': lazy_reverse('donation.add'),
        'search': lazy_reverse('donation.search'),
    }

site.register(Donation, DonationRegistry)
