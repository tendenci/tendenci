from rss.feedsmanager import SubFeed
from site_settings.utils import get_setting
from perms.utils import PUBLIC_FILTER
from sitemaps import TendenciSitemap

from S_P_LOW.models import S_S_CAP

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest S_P_CAP' % get_setting('site','global','sitedisplayname')
    link =  "/S_P_LOW/"
    description =  "Latest S_P_CAP by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        items = S_S_CAP.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')[:20]
        return items

    def item_title(self, item):
        return item.S_S_LOW

    def item_description(self, item):
        return item.S_S_LOW

    def item_pubdate(self, item):
        return item.create_dt

    def item_link(self, item):
        return item.get_absolute_url()

class S_S_CAPSitemap(TendenciSitemap):
    """ Sitemap information for S_P_LOW """
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        items = S_S_CAP.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')[:20]
        return items

    def lastmod(self, obj):
        return obj.create_dt
    