from rss.feedsmanager import SubFeed
from site_settings.utils import get_setting
from perms.utils import PUBLIC_FILTER
from sitemaps import TendenciSitemap

from speakers.models import Speaker

class LatestEntriesFeed(SubFeed):
    title =  'Latest Speaker'
    link =  "/speakers/"
    description =  "Latest Speaker"

    def items(self):
        items = Speaker.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')[:20]
        return items

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.biography

    def item_pubdate(self, item):
        return item.create_dt

    def item_link(self, item):
        return item.get_absolute_url()

class SpeakerSitemap(TendenciSitemap):
    """ Sitemap information for speakers """
    changefreq = "monthly"
    priority = 0.5
    
    def items(self):
        items = Speaker.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')
        return items
    
    def lastmod(self, obj):
        return obj.update_dt
