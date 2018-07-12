from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import AppRegistry, lazy_reverse
from tendenci.apps.donations.models import Donation


class DonationRegistry(AppRegistry):
    version = '1.0'
    author = 'Tendenci - The Open Source AMS for Associations'
    author_email = 'programmers@tendenci.com'
    description = 'Allow donations from anyone'

    url = {
        'add': lazy_reverse('donation.add'),
        'search': lazy_reverse('donation.search'),
    }

site.register(Donation, DonationRegistry)
