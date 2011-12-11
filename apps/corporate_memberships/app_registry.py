from registry import site
from registry.base import PeopleRegistry, lazy_reverse
from models import CorporateMembership


class CorporateMembershipRegistry(PeopleRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Corporate membership management application.'
    icon = '/site_media/static/images/icons/corporate-membership-color-64x64.png'

    url = {
        'search': lazy_reverse('corp_memb.search'),
    }

site.register(CorporateMembership, CorporateMembershipRegistry)
