from tendenci.apps.rss.feedsmanager import SubFeed
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.perms.utils import PUBLIC_FILTER
from tendenci.apps.sitemaps import TendenciSitemap

from tendenci.apps.studygroups.models import StudyGroup

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest StudyGroups' % get_setting('site','global','sitedisplayname')
    link =  "/studygroups/"
    description =  "Latest StudyGroups by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        items = StudyGroup.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')[:20]
        return items

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content

    def item_pubdate(self, item):
        return item.create_dt

    def item_link(self, item):
        return item.get_absolute_url()

class StudyGroupSitemap(TendenciSitemap):
    """ Sitemap information for studygroups """
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        items = StudyGroup.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')
        return items

    def lastmod(self, obj):
        return obj.create_dt
