from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from tendenci.core.registry import site
from tendenci.core.registry.base import CoreRegistry, lazy_reverse
from tendenci.core.files.models import File


class FileRegistry(CoreRegistry):
    version = '1.0'
    author = _('Schipul - The Web Marketing Company')
    author_email = 'programmers@schipul.com'
    description = _('Stores file links and infomation for files ' \
                  'uploaded through wysiwyg and other parts in ' \
                  'the system')
    icon = '%simages/icons/files-color-64x64.png' % settings.STATIC_URL

    event_logs = {
        'files':{
            'base':('180000','330066'),
            'add':('181000','330066'),
            'edit':('182000','330066'),
            'delete':('183000','330066'),
            'view':('185000','330066'),
            'download':('186000','330066'),
        }
    }

    url = {
        'add': lazy_reverse('file.add'),
        'search': lazy_reverse('files'),
    }

site.register(File, FileRegistry)
