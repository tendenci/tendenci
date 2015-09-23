from tendenci.apps.rss.feedsmanager import SubFeed
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.perms.utils import PUBLIC_FILTER
from tendenci.apps.sitemaps import TendenciSitemap

from tendenci.apps.videos.models import Video

class LatestEntriesFeed(SubFeed):
    title =  'Latest Videos'
    link =  "/videos/"
    description =  "Latest Videos"

    def items(self):
        items = Video.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')[:20]
        return items

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.embed_code()+item.description

    def item_pubdate(self, item):
        return item.create_dt

    def item_link(self, item):
        return item.get_absolute_url()

class VideoSitemap(TendenciSitemap):
    """ Sitemap information for videos """
    changefreq = "monthly"
    priority = 0.5
    
    def items(self):
        items = Video.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')
        return items

    def lastmod(self, obj):
        return obj.create_dt
