from django.contrib.syndication.views import Feed

from site_settings.utils import get_setting
from contributions.models import Contribution

class LatestEntriesFeed(Feed):
    title =  '%s Latest Contributions' % get_setting('site','global','sitedisplayname')
    link =  "/contributions/"
    description =  "Latest Contributions by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        return Contribution.objects.order_by('-create_dt')[:20]
    
    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.title

    def item_link(self, item):
        return item.object().get_absolute_url()