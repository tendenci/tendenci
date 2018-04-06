from datetime import datetime

from django.contrib.syndication.views import Feed
from django.conf import settings


class SubFeed(Feed):

    def __init__(self):
        super(SubFeed, self).__init__()
        self.__qualname__ = self.__class__.__name__  # https://code.djangoproject.com/ticket/29296

    def items(self):
        return []

    def item_title(self, item):
        return ''

    def item_description(self, item):
        return ''

    def item_link(self, item):
        return ''

    def item_author_name(self, item):
        return ''

    def item_pubdate(self, item):
        return datetime.now()

_feeds_cache = []


def get_all_feeds():
    for app in settings.INSTALLED_APPS:
        _try_import(app + '.feeds')
    return SubFeed.__subclasses__()


def _try_import(module):
    try:
        __import__(module)
    except ImportError:
        pass
        #print("Failed to import feeds file: %s" % e)
