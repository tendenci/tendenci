from tendenci.core.rss.feedsmanager import SubFeed
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.perms.utils import PUBLIC_FILTER
from tendenci.core.sitemaps import TendenciSitemap

from tendenci.apps.services.models import Service

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest Services' % get_setting('site','global','sitedisplayname')
    link =  "/resumes/"
    description =  "Latest Services by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        items = Service.objects.filter(**PUBLIC_FILTER).filter(syndicate=True).order_by('-create_dt')[:20]
        return items

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_pubdate(self, item):
        return item.create_dt

    def item_link(self, item):
        return item.get_absolute_url()

class ServiceSitemap(TendenciSitemap):
    """ Sitemap information for services """
    changefreq = "monthly"
    priority = 0.5
    
    def items(self):
        items = Service.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')
        return items

    def lastmod(self, obj):
        return obj.create_dt
