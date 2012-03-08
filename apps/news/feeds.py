from datetime import datetime

from rss.feedsmanager import SubFeed
from site_settings.utils import get_setting
from perms.utils import PUBLIC_FILTER
from sitemaps import TendenciSitemap

from news.models import News

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest News' % get_setting('site','global','sitedisplayname')
    link =  "/news/"
    description =  "Latest News by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        items = News.objects.filter(**PUBLIC_FILTER).filter(syndicate=True, release_dt__lte=datetime.now()).order_by('-release_dt')[:20]
        return items
    
    def item_title(self, item):
        return item.headline

    def item_description(self, item):
        return item.body

    def item_pubdate(self, item):
        return item.release_dt

    def item_link(self, item):
        return item.get_absolute_url()

class NewsSitemap(TendenciSitemap):
    """ Sitemap information for news """
    changefreq = "monthly"
    priority = 0.5
    
    def items(self):
        items = News.objects.filter(**PUBLIC_FILTER).filter(release_dt__lte=datetime.now()).order_by('-release_dt')
        return items

    def lastmod(self, obj):
        return obj.create_dt