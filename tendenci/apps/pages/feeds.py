from tendenci.apps.rss.feedsmanager import SubFeed
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.perms.utils import PUBLIC_FILTER
from tendenci.apps.sitemaps import TendenciSitemap

from tendenci.apps.pages.models import Page
from django.utils.translation import ugettext_lazy as _

class LatestEntriesFeed(SubFeed):
    title =  _('%(dname)s Latest Pages' % {'dname':get_setting('site','global','sitedisplayname')})
    link =  "/pages/"
    description =  _("Latest Pages by %(dname)s" % {'dname':get_setting('site','global','sitedisplayname')})

    def items(self):
        items = Page.objects.filter(**PUBLIC_FILTER).filter(syndicate=True).order_by('-create_dt')[:20]
        return items

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content

    def item_pubdate(self, item):
        return item.create_dt

    def item_link(self, item):
        return item.get_absolute_url()

class PageSitemap(TendenciSitemap):
    """ Sitemap information for pages """
    changefreq = "yearly"
    priority = 0.6

    def items(self):
        items = Page.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')
        return items

    def lastmod(self, obj):
        return obj.update_dt
