from rss.feedsmanager import SubFeed
from site_settings.utils import get_setting
from perms.utils import PUBLIC_FILTER
from sitemaps import TendenciSitemap

from products.models import Product

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest Products' % get_setting('site','global','sitedisplayname')
    link =  "/products/"
    description =  "Latest Products by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        items = Product.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')[:20]
        return items

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description

    def item_pubdate(self, item):
        return item.create_dt

    def item_link(self, item):
        return item.get_absolute_url()

class ProductSitemap(TendenciSitemap):
    """ Sitemap information for products """
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        items = Product.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')
        return items

    def lastmod(self, obj):
        return obj.create_dt
