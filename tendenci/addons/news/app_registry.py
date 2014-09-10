from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from tendenci.core.registry import site
from tendenci.core.registry.base import CoreRegistry, lazy_reverse
from tendenci.addons.news.models import News


class NewsRegistry(CoreRegistry):
    version = '1.0'
    author = _('Schipul - The Web Marketing Company')
    author_email = 'programmers@schipul.com'
    description = _('Create news to let your vistors keep current')
    icon = '%simages/icons/news-color-64x64.png' % settings.STATIC_URL

    event_logs = {
        'news':{
            'base':('305000', 'FF0033'),
            'add':('305100', 'FF0033'),
            'edit':('305200', 'FF0033'),
            'delete':('305300', 'FF0033'),
            'search':('305400', 'FF0033'),
            'view':('305500', '8C0000'),
            'print_view':('305501', '8C0000'),
        }
    }

    url = {
        'add': lazy_reverse('news.add'),
        'search': lazy_reverse('news'),
    }

site.register(News, NewsRegistry)
