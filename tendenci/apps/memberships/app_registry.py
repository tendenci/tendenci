from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import PeopleRegistry, lazy_reverse
from tendenci.apps.memberships.models import MembershipDefault


class MembershipRegistry(PeopleRegistry):
    version = '1.0'
    author = _('Schipul - The Web Marketing Company')
    author_email = 'programmers@schipul.com'
    description = _('Membership management application.')
    icon = '%simages/icons/memberships-color-64x64.png' % settings.STATIC_URL

    event_logs = {
        'membership':{
            'base':('470000','333366'),
            'add':('471000','333366'),
            'edit':('472000','333366'),
            'delete':('473000','333366'),
            'search':('474000','333366'),
            'view':('475000','333366'),
            'export':('475105','333366'),
        },
        'membership_type':{
            'base':('475100','333366'),
            'edit':('475200','333366'),
            'delete':('475300','333366'),
            'search':('475400','333366'),
            'view':('475500','333366'),
        },
        'membership_application':{
            'base':('650000','FF0066'),
            'add':('651000','FF0066'),
            'edit':('652000','FF3366'),
            'delete':('653000','FF0099'),
            'search':('654000','FF3399'),
            'view':('655000','FF00CC'),
        },
        'membership_application_fields':{
            'base':('660000','FF6633'),
            'add':('661000','FF6633'),
            'edit':('662000','FF3366'),
            'delete':('663000','FF9933'),
            'search':('664000','FF6666'),
            'view':('665000','FF9966'),
        },
        'membership_entries':{
            'base':('1080000','FF6633'),
            'add':('1081000','FF6633'),
            'search':('1084000','FF6633'),
            'view':('1085000','FF6633'),
            'approved':('1082101','FF6633'),
            'disapproved':('1082102','FF6633'),
        },
        'membership notice':{
            'base':('900000','FFFF00'),
            'add':('901000','FFDB00'),
            'edit':('902000','FFB600'),
            'delete':('903000','FF9200'),
            'search':('904000','FF6D00'),
            'view':('905000','FF4900'),
            'print_view':('906000','FF2400'),
        }
    }

    url = {
        'add': lazy_reverse('admin:memberships_membershipapp_changelist'),
        'list': lazy_reverse('membership.index'),
        'search': lazy_reverse('membership.search'),
    }

site.register(MembershipDefault, MembershipRegistry)
