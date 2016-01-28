from tendenci.apps.rss.feedsmanager import SubFeed
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.perms.utils import PUBLIC_FILTER
from tendenci.apps.sitemaps import TendenciSitemap

from tendenci.apps.projects.models import Project

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest Projects' % get_setting('site','global','sitedisplayname')
    link =  "/projects/"
    description =  "Latest Projects by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        items = Project.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')[:20]
        return items

    def item_title(self, item):
        return item.author

    def item_description(self, item):
        return item.project

    def item_pubdate(self, item):
        return item.create_dt

    def item_link(self, item):
        return item.get_absolute_url()

class ProjectSitemap(TendenciSitemap):
    """ Sitemap information for projects """
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        items = Project.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')
        return items

    def lastmod(self, obj):
        return obj.create_dt
