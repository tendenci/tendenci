from registry import site
from registry.base import PeopleRegistry, lazy_reverse
from models import CorporateMembership


class CorporateMembershipRegistry(PeopleRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Corporate membership management application.'
    icon = '/site_media/static/images/icons/corporate-membership-color-64x64.png'
    
    event_logs = {
        'corporate_membership':{
            'base':('680000','3300FF'),
            'add':('681000','3300FF'),
            'renew':('681001','471DEF'),
            'edit':('682000','1F85FF'),
            'join_approval':('682001','4D29DF'),
            'renewal_approval':('682002','5233CF'),
            'join_disapproval':('682003','563BBF'),
            'renewal_disapproval':('682004','7A6DAF'),
            'delete':('683000','B0A8CF'),
            'import':('689005','47A0BF'),
        }
    }

    url = {
        'search': lazy_reverse('corp_memb.search'),
    }

site.register(CorporateMembership, CorporateMembershipRegistry)
