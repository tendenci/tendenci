from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import News


class NewsRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create news to let your vistors keep current'
    icon = '/site_media/static/images/icons/news-color-64x64.png'
    
    #Event log
    base_id = '305000'
    base_color = 'FF0033'
    add_id = '305100'
    add_color = 'FF0033'
    edit_id = '305200'
    edit_color = 'FF0033'
    delete_id = '305300'
    delete_color = 'FF0033'
    search_id = '305400'
    search_color = 'FF0033'
    view_id = '305500'
    view_color = '8C0000'
    print_view_id = '305501'
    print_view_color = '8C0000'

    url = {
        'add': lazy_reverse('news.add'),
        'search': lazy_reverse('news.search'),
    }

site.register(News, NewsRegistry)
