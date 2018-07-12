from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import AppRegistry, lazy_reverse
from tendenci.apps.committees.models import Committee


class CommitteeRegistry(AppRegistry):
    version = '1.0'
    author = 'Tendenci - The Open Source AMS for Associations'
    author_email = 'programmers@tendenci.com'
    description = 'Create committees type of content'

    url = {
        'add': lazy_reverse('committees.add'),
        'search': lazy_reverse('committees.search'),
    }

site.register(Committee, CommitteeRegistry)
