from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from tendenci.core.registry import site
from tendenci.core.registry.base import PeopleRegistry, lazy_reverse
from tendenci.apps.user_groups.models import Group


class GroupRegistry(PeopleRegistry):
    version = '1.0'
    author = _('Schipul - The Web Marketing Company')
    author_email = 'programmers@schipul.com'
    description = _('User Groups.')
    icon = '%simages/icons/groups-color-64x64.png' % settings.STATIC_URL

    event_logs = {
        'group':{
            'base':('160000','339999'),
            'add':('161000','339999'),
            'edit':('162000','339999'),
            'delete':('163000','339999'),
            'search':('164000','339999'),
            'view':('165000','339999'),
        },
        'groupmembership':{
            'base':('220000','00CCFF'),
            'add':('221000','00CCFF'),
            'edit':('222000','00CCFF'),
            'delete':('223000','00CCFF'),
            'search':('224000','00CCFF'),
            'view':('225000','00CCFF'),
        }
    }

    url = {
        'search': lazy_reverse('groups'),
        'add': lazy_reverse('group.add'),
    }

site.register(Group, GroupRegistry)
