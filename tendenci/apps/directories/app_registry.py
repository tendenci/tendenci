from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import CoreRegistry, lazy_reverse
from tendenci.apps.directories.models import Directory


class DirectoryRegistry(CoreRegistry):
    version = '1.0'
    author = _('Schipul - The Web Marketing Company')
    author_email = 'programmers@schipul.com'
    description = _('Create directories to list businesses')
    icon = '%simages/icons/directories-color-64x64.png' % settings.STATIC_URL

    event_logs = {
        'directory':{
            'base':('440000','CCCC33'),
            'add':('441000','CCCC33'),
            'edit':('442000','CCCC33'),
            'delete':('443000','CCCC33'),
            'search':('444000','CCCC33'),
            'view':('445000','CCCC33'),
            'print_view':('445001','CCCC33'),
            'renew':('442210','CCCC33'),
        }
    }

    url = {
        'add': lazy_reverse('directory.add'),
        'search': lazy_reverse('directories'),
        'list': lazy_reverse('directories'),
    }

site.register(Directory, DirectoryRegistry)
