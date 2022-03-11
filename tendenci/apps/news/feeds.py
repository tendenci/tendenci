from datetime import datetime
from django.utils.translation import gettext_lazy as _

from tendenci.apps.rss.feedsmanager import SubFeed
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.perms.utils import PUBLIC_FILTER
from tendenci.apps.sitemaps import TendenciSitemap

from tendenci.apps.news.models import News
from tendenci.apps.base.decorators import strip_control_chars

class LatestEntriesFeed(SubFeed):
    title =  _('%(dname)s Latest News' % {'dname': get_setting('site','global','sitedisplayname')})
    link =  "/news/"
    description =  _("Latest News by %(dname)s" % {'dname': get_setting('site','global','sitedisplayname')})

    def items(self):
        items = News.objects.filter(**PUBLIC_FILTER).filter(syndicate=True, release_dt__lte=datetime.now()).order_by('-release_dt')[:20]
        return items

    @strip_control_chars
    def item_title(self, item):
        return item.headline

    @strip_control_chars
    def item_description(self, item):
        return item.body

    def item_pubdate(self, item):
        return item.release_dt

    @strip_control_chars
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
        return obj.release_dt
