from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import News


class NewsRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create news to let your vistors keep current'
    icon = '/site_media/static/images/icons/news-color-64x64.png'

    url = {
        'add': lazy_reverse('news.add'),
        'search': lazy_reverse('news.search'),
    }

site.register(News, NewsRegistry)
