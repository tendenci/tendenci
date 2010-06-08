from django.contrib.syndication.views import Feed

from site_settings.utils import get_setting
from news.models import News

class LatestEntriesFeed(Feed):
    title =  '%s Latest News' % get_setting('site','global','sitedisplayname')
    link =  "/news/"
    description =  "Latest News by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        return News.objects.order_by('-create_dt')[:20]
    
    def item_title(self, item):
        return item.headline

    def item_description(self, item):
        return item.body