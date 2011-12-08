from registry import site
from registry.base import PeopleRegistry, lazy_reverse
from models import Profile


class ProfileRegistry(PeopleRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'User Profiles.'
    icon = '/site_media/static/images/icons/users-color-64x64.png'

    url = {
        'search': lazy_reverse('profile.search'),
        'add': lazy_reverse('profile.add'),
    }

site.register(Profile, ProfileRegistry)
