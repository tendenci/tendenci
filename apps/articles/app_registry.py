from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import Article


class ArticleRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create articles to display basic content ' \
                  'throughout the site'
    icon = '/site_media/static/images/icons/articles-color-64x64.png'
    
    # Event Logs
    base_id = '430000'
    base_color = 'CC9966'
    add_id = '431000'
    add_color = 'CC9966'
    edit_id = '432000'
    edit_color = 'CCCC66'
    delete_id = '433000'
    delete_color = 'CCCC00'
    search_id = '434000'
    search_color = 'CCCC33'
    view_id = '435000'
    view_color = 'CCCC99'
    print_view_id = '435001'
    pring_view_color = 'FFCC99'

    url = {
        'add': lazy_reverse('article.add'),
        'search': lazy_reverse('article.search'),
    }

site.register(Article, ArticleRegistry)
