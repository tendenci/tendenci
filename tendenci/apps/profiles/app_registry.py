from django.utils.translation import ugettext as _

from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import PeopleRegistry, lazy_reverse
from tendenci.apps.profiles.models import Profile
from tendenci.apps.theme.templatetags.static import static


class ProfileRegistry(PeopleRegistry):
    version = '1.0'
    author = _('Tendenci - The Open Source AMS for Associations')
    author_email = 'programmers@tendenci.com'
    description = _('User Profiles.')
    icon = static('images/icons/users-color-64x64.png')

    event_logs = {
        'profile':{
            'base':('120000','3300FF'),
            'add':('121000','3300FF'),
            'edit':('122000', '3333FF'),
            'delete':('123000', '3366FF'),
            'search':('124000', '3366FF'),
            'view':('125000', '3399FF'),
        },
    }

    url = {
        'search': lazy_reverse('profile.search'),
        'add': lazy_reverse('profile.add'),
        'settings': lazy_reverse('settings.index', args=['module','users']),
    }

site.register(Profile, ProfileRegistry)
