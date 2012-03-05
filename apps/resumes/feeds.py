from rss.feedsmanager import SubFeed
from site_settings.utils import get_setting
from perms.utils import PUBLIC_FILTER
from sitemaps import TendenciSitemap

from resumes.models import Resume

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest Resumes' % get_setting('site','global','sitedisplayname')
    link =  "/resumes/"
    description =  "Latest Resumes by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        items = Resume.objects.filter(**PUBLIC_FILTER).filter(syndicate=True).order_by('-create_dt')[:20]
        return items

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_pubdate(self, item):
        return item.create_dt

    def item_link(self, item):
        return item.get_absolute_url()

class ResumeSitemap(TendenciSitemap):
    """ Sitemap information for resumes """
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        items = Resume.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')
        return items

    def lastmod(self, obj):
        return obj.create_dt
