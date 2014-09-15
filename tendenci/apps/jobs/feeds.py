from django.utils.translation import ugettext_lazy as _

from tendenci.apps.rss.feedsmanager import SubFeed
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.perms.utils import PUBLIC_FILTER
from tendenci.apps.sitemaps import TendenciSitemap

from tendenci.apps.jobs.models import Job

class LatestEntriesFeed(SubFeed):
    title = _('%(dname)s Latest Jobs' % {'dname': get_setting('site','global','sitedisplayname')})
    link =  "/jobs/"
    description = _("Latest Jobs by %(dname)s" % {'dname' : get_setting('site','global','sitedisplayname')})

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
