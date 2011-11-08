from rss.feedsmanager import SubFeed
from haystack.query import SearchQuerySet

from site_settings.utils import get_setting
from plugs.models import Plug
from sitemaps import TendenciSitemap

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest Plugs' % get_setting('site','global','sitedisplayname')
    link =  "/plugs/"
    description =  "Latest Plugs by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        sqs = SearchQuerySet().filter(can_syndicate=True).models(Plug).order_by('-create_dt')[:20]
        return [sq.object for sq in sqs]

    def item_title(self, item):
        return item.author

    def item_description(self, item):
        return item.plug

    def item_link(self, item):
        return item.get_absolute_url()

class PlugSitemap(TendenciSitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        sqs = SearchQuerySet().models(Plug).order_by('-create_dt')
        return [sq.object for sq in sqs]

    def lastmod(self, obj):
        return obj.create_dt
    