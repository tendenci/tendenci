from django.contrib.syndication.views import Feed

from site_settings.utils import get_setting
from events.models import Event

class LatestEntriesFeed(Feed):
    title =  '%s Latest Events' % get_setting('site','global','sitedisplayname')
    link =  "/events/"
    description =  "Latest Events by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        return Event.objects.order_by('-create_dt')[:20]
    
    def item_title(self, item):
        return item.headline

    def item_description(self, item):
        return item.body