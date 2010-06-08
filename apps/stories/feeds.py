from django.contrib.syndication.views import Feed

from site_settings.utils import get_setting
from stories.models import Story

class LatestEntriesFeed(Feed):
    title =  '%s Latest Stories' % get_setting('site','global','sitedisplayname')
    link =  "/stories/"
    description =  "Latest Stories by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        return Story.objects.order_by('-create_dt')[:20]
    
    def item_title(self, item):
        return item.headline

    def item_description(self, item):
        return item.body