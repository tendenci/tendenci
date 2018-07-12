from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import AppRegistry, lazy_reverse

from tendenci.apps.staff.models import Staff


class StaffRegistry(AppRegistry):
    version = '1.0'
    author = 'Tendenci - The Open Source AMS for Associations'
    author_email = 'programmers@tendenci.com'
    description = 'Create staff biographies easily with photo,' \
                  ' position, tagline and more ..'

    event_logs = {
        'staff':{
            'base':('1080000','EE7733'),
            'add':('1080100','119933'),
            'edit':('1080200','EEDD55'),
            'delete':('1080300','AA2222'),
            'search':('1080400','CC55EE'),
            'view':('1080500','55AACC'),
        }
    }

    url = {
        'add': lazy_reverse('admin:staff_staff_add'),
        'search': lazy_reverse('staff'),
        'list': lazy_reverse('staff'),
    }

site.register(Staff, StaffRegistry)
