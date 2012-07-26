from tendenci.core.rss.feedsmanager import SubFeed
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.perms.utils import PUBLIC_FILTER
from tendenci.core.sitemaps import TendenciSitemap

from tendenci.apps.museums.models import Museum

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest Museums' % get_setting('site','global','sitedisplayname')
    link =  "/museums/"
    description =  "Latest Museums by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        items = Museum.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')[:20]
        return items

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.about

    def item_pubdate(self, item):
        return item.create_dt

    def item_link(self, item):
        return item.get_absolute_url()

class MuseumSitemap(TendenciSitemap):
    """ Sitemap information for museum """
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        items = Museum.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')
        return items

    def lastmod(self, obj):
        return obj.create_dt
    
