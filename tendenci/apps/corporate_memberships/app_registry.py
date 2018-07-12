from django.utils.translation import ugettext_lazy as _

from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import PeopleRegistry, lazy_reverse
from tendenci.apps.corporate_memberships.models import CorpMembership
from tendenci.apps.theme.templatetags.static import static


class CorpMembershipRegistry(PeopleRegistry):
    version = '1.0'
    author = _('Tendenci - The Open Source AMS for Associations')
    author_email = 'programmers@tendenci.com'
    description = _('Corporate membership management application.')
    icon = static('images/icons/corporate-membership-color-64x64.png')

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
        'add': lazy_reverse('corpmembership.add'),
        'search': lazy_reverse('corpmembership.search'),
#        'list': lazy_reverse('corpmembership.search')
    }

site.register(CorpMembership, CorpMembershipRegistry)
