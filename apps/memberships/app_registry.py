from registry import site
from registry.base import PeopleRegistry, lazy_reverse
from models import Membership


class MembershipRegistry(PeopleRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Membership management application.'
    icon = '/site_media/static/images/icons/memberships-color-64x64.png'

    url = {
        'search': lazy_reverse('membership.search'),
    }

site.register(Membership, MembershipRegistry)
