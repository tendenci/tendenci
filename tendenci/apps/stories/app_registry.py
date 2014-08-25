from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from tendenci.core.registry import site
from tendenci.core.registry.base import CoreRegistry, lazy_reverse
from tendenci.apps.stories.models import Story


class StoryRegistry(CoreRegistry):
    version = '1.0'
    author = _('Schipul - The Web Marketing Company')
    author_email = 'programmers@schipul.com'
    description = _('Stories can be created and rotated on ' \
                  'a specified area on the site')
    icon = '%simages/icons/stories-color-64x64.png' % settings.STATIC_URL

    event_logs = {
        'story':{
            'base':('1060000','FF33FF'),
            'add':('1060100','FF33FF'),
            'edit':('1060200','DD77AA'),
            'delete':('1060300','CC9980'),
            'search':('1060400','AADD2B'),
            'view':('1060500','99FF00'),
            'print_view':('1060501', '99FF00'),
        },
    }

    url = {
        'add': lazy_reverse('story.add'),
        'search': lazy_reverse('stories'),
    }

site.register(Story, StoryRegistry)
