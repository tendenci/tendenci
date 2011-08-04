from rss.feedsmanager import SubFeed
from haystack.query import SearchQuerySet

from site_settings.utils import get_setting
from S_P_LOW.models import S_S_CAP
from sitemaps import TendenciSitemap

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest S_P_CAP' % get_setting('site','global','sitedisplayname')
    link =  "/S_P_LOW/"
    description =  "Latest S_P_CAP by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        sqs = SearchQuerySet().filter(can_syndicate=True).models(S_S_CAP).order_by('-create_dt')[:20]
        return [sq.object for sq in sqs]

    def item_title(self, item):
        return item.author

    def item_description(self, item):
        return item.S_S_LOW

    def item_link(self, item):
        return item.get_absolute_url()

class S_S_CAPSitemap(TendenciSitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        sqs = SearchQuerySet().models(S_S_CAP).order_by('-create_dt')
        return [sq.object for sq in sqs]

    def lastmod(self, obj):
        return obj.create_dt
    