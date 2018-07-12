from django.utils.translation import ugettext_lazy as _

from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import CoreRegistry, lazy_reverse
from tendenci.apps.files.models import File
from tendenci.apps.theme.templatetags.static import static


class FileRegistry(CoreRegistry):
    version = '1.0'
    author = _('Tendenci - The Open Source AMS for Associations')
    author_email = 'programmers@tendenci.com'
    description = _('Stores file links and infomation for files '
                  'uploaded through wysiwyg and other parts in '
                  'the system')
    icon = static('images/icons/files-color-64x64.png')

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
