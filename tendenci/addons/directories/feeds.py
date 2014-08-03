from django.utils.translation import ugettext_lazy as _

from tendenci.core.rss.feedsmanager import SubFeed
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.perms.utils import PUBLIC_FILTER
from tendenci.core.sitemaps import TendenciSitemap

from tendenci.addons.directories.models import Directory

class LatestEntriesFeed(SubFeed):
    title = _('%(sitedisplayname)s Latest Directories') % {
        'sitedisplayname': get_setting('site', 'global', 'sitedisplayname')}
    link =  "/directories/"
    description = _("Latest Directories by %(sitedisplayname)s") % {
        'sitedisplayname': get_setting('site', 'global', 'sitedisplayname')}

    def items(self):
        items = Directory.objects.filter(**PUBLIC_FILTER).filter(syndicate=True).order_by('-create_dt')[:20]
        return items

    def item_title(self, item):
        return item.headline

    def item_description(self, item):
        return item.body

    def item_pubdate(self, item):
        return item.create_dt

    def item_link(self, item):
        return item.get_absolute_url()

class DirectorySitemap(TendenciSitemap):
    """ Sitemap information for directories """
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        items = Directory.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')
        return items

    def lastmod(self, obj):
        return obj.create_dt
