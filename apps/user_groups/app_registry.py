from registry import site
from registry.base import PeopleRegistry, lazy_reverse
from models import Group


class GroupRegistry(PeopleRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'User Groups.'
    icon = '/site_media/static/images/icons/groups-color-64x64.png'

    url = {
        'search': lazy_reverse('group.search'),
        'add': lazy_reverse('group.add'),
    }

site.register(Group, GroupRegistry)
