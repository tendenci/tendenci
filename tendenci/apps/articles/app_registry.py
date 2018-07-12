from django.utils.translation import ugettext_lazy as _

from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import CoreRegistry, lazy_reverse
from tendenci.apps.articles.models import Article
from tendenci.apps.theme.templatetags.static import static


class ArticleRegistry(CoreRegistry):
    version = _('1.0')
    author = _('Tendenci - The Open Source AMS for Associations')
    author_email = 'programmers@tendenci.com'
    description = _('Create articles to display basic content throughout the site')
    icon = static('images/icons/articles-color-64x64.png')

    event_logs = {
        'article': {
            'base': ('430000', 'CC9966'),
            'add': ('431000', 'CC9966'),
            'edit': ('432000', 'CCCC66'),
            'delete': ('433000', 'CCCC00'),
            'search': ('434000', 'CCCC33'),
            'view': ('435000', 'CCCC99'),
            'print_view': ('435001', 'FFCC99'),
        }
    }

    url = {
        'add': lazy_reverse('article.add'),
        'search': lazy_reverse('articles'),
        'list': lazy_reverse('articles'),
    }

site.register(Article, ArticleRegistry)
