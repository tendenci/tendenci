from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import News


class NewsRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create news to let your vistors keep current'
    icon = '/site_media/static/images/icons/news-color-64x64.png'
    
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
