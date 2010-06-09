from django.contrib.syndication.views import Feed

from site_settings.utils import get_setting
from articles.models import Article

class LatestEntriesFeed(Feed):
    title =  '%s Latest Articles' % get_setting('site','global','sitedisplayname')
    link =  "/articles/"
    description =  "Latest Articles by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        return Article.objects.order_by('-create_dt')[:20]
    
    def item_title(self, item):
        return item.headline

    def item_description(self, item):
        return item.body