from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import Article


class ArticleRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create articles to display basic content throughout the site'
    icon = '/site_media/static/images/icons/articles-color-64x64.png'
    
    event_logs = {
        'article':{
            'base':('430000', 'CC9966'),
            'add':('431000', 'CC9966'),
            'edit':('432000', 'CCCC66'),
            'delete':('433000', 'CCCC00'),
            'search':('434000', 'CCCC33'),
            'view':('435000', 'CCCC99'),
            'print_view':('435001', 'FFCC99'),
        }
    }
    
    url = {
        'add': lazy_reverse('article.add'),
        'search': lazy_reverse('articles'),
        'list': lazy_reverse('articles'),
    }

site.register(Article, ArticleRegistry)
