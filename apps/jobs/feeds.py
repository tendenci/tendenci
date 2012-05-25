from rss.feedsmanager import SubFeed
from site_settings.utils import get_setting
from perms.utils import PUBLIC_FILTER
from sitemaps import TendenciSitemap

from jobs.models import Job

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest Jobs' % get_setting('site','global','sitedisplayname')
    link =  "/jobs/"
    description =  "Latest Jobs by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        items = Job.objects.filter(**PUBLIC_FILTER).filter(syndicate=True).order_by('-update_dt')[:20]
        return items
    
    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_pubdate(self, item):
        return item.update_dt

    def item_link(self, item):
        return item.get_absolute_url()

class JobSitemap(TendenciSitemap):
    """ Sitemap information for jobs """
    changefreq = "monthly"
    priority = 0.5
    
    def items(self):     
        items = Job.objects.filter(**PUBLIC_FILTER).order_by('-update_dt')
        return items

    def lastmod(self, obj):
        return obj.update_dt
