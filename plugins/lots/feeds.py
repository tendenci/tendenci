from rss.feedsmanager import SubFeed
from site_settings.utils import get_setting
from perms.utils import PUBLIC_FILTER
from sitemaps import TendenciSitemap

from lots.models import Lot

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest Lots' % get_setting('site','global','sitedisplayname')
    link =  "/lots/"
    description =  "Latest Lots by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        items = Lot.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')[:20]
        return items

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description

    def item_pubdate(self, item):
        return item.create_dt

    def item_link(self, item):
        return item.get_absolute_url()

class LotSitemap(TendenciSitemap):
    """ Sitemap information for lots """
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        items = Lot.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')
        return items

    def lastmod(self, obj):
        return obj.create_dt
