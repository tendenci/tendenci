from rss.feedsmanager import SubFeed
from site_settings.utils import get_setting
from models import Service
from sitemaps import TendenciSitemap

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest Services' % get_setting('site','global','sitedisplayname')
    link =  "/resumes/"
    description =  "Latest Services by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        return Service.objects.order_by('-create_dt')[:20]
    
    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description


class ServiceSitemap(TendenciSitemap):
    changefreq = "monthly"
    priority = 0.5
    
    def items(self):
        return Service.objects.order_by('-create_dt')
                                        
    def lastmod(self, obj):
        return obj.create_dt
    