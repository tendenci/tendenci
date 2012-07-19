from rss.feedsmanager import SubFeed
from site_settings.utils import get_setting
from perms.utils import PUBLIC_FILTER
from sitemaps import TendenciSitemap

from help_files.models import HelpFile

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest Helpfiles' % get_setting('site','global','sitedisplayname')
    link =  "/help-files/"
    description =  "Latest Helpfiles by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        items = HelpFile.objects.filter(**PUBLIC_FILTER).filter(syndicate=True).order_by('-create_dt')[:20]
        return items

    def item_title(self, item):
        return item.question

    def item_description(self, item):
        return item.answer

    def item_pubdate(self, item):
        return item.create_dt

    def item_link(self, item):
        return item.get_absolute_url()

class HelpFileSitemap(TendenciSitemap):
    """ Sitemap information for help files """
    changefreq = "monthly"
    priority = 0.5
    
    def items(self):     
        items = HelpFile.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')
        return items

    def lastmod(self, obj):
        return obj.create_dt
