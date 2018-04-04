from django.utils.translation import ugettext_lazy as _

from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import CoreRegistry, lazy_reverse
from tendenci.apps.forums.models import Forum
from tendenci.apps.theme.templatetags.static import static


class ForumRegistry(CoreRegistry):
    version = _('1.0')
    author = _('Tendenci')
    author_email = 'programmers@tendenci.com'
    description = _("Forums")
    icon = static('images/icons/forums-color-64x64.png')

    url = {
        'list': lazy_reverse('pybb:index'),
    }

site.register(Forum, ForumRegistry)
