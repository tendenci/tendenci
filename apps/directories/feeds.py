from django.contrib.syndication.views import Feed

from site_settings.utils import get_setting
from directories.models import Directory

class LatestEntriesFeed(Feed):
    title =  '%s Latest Directories' % get_setting('site','global','sitedisplayname')
    link =  "/directories/"
    description =  "Latest Directories by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        return Directory.objects.order_by('-create_dt')[:20]
    
    def item_title(self, item):
        return item.headline

    def item_description(self, item):
        return item.body