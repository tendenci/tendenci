from django.utils.translation import ugettext_lazy as _

from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import CoreRegistry, lazy_reverse
from tendenci.apps.stories.models import Story
from tendenci.apps.theme.templatetags.static import static


class StoryRegistry(CoreRegistry):
    version = '1.0'
    author = _('Tendenci - The Open Source AMS for Associations')
    author_email = 'programmers@tendenci.com'
    description = _('Stories can be created and rotated on '
                  'a specified area on the site')
    icon = static('images/icons/stories-color-64x64.png')

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
