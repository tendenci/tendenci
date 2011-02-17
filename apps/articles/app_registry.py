from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import Article


class ArticleRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create articles to display basic content ' \
                  'throughout the site'

    url = {
        'add': lazy_reverse('article.add'),
        'search': lazy_reverse('article.search'),
    }

site.register(Article, ArticleRegistry)
