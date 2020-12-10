from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import AppRegistry, lazy_reverse
from tendenci.apps.chapters.models import Chapter


class ChapterRegistry(AppRegistry):
    version = '1.0'
    author = 'Tendenci - The Open Source AMS for Associations'
    author_email = 'programmers@tendenci.com'
    description = 'Create chapters type of content'

    url = {
        'add': lazy_reverse('chapters.add'),
        'search': lazy_reverse('chapters.search'),
    }

site.register(Chapter, ChapterRegistry)
