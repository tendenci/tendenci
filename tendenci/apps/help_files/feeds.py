from django.utils.translation import gettext_lazy as _

from tendenci.apps.rss.feedsmanager import SubFeed
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.perms.utils import PUBLIC_FILTER
from tendenci.apps.sitemaps import TendenciSitemap

from tendenci.apps.help_files.models import HelpFile

class LatestEntriesFeed(SubFeed):
    title = _('%(hp)s Latest Helpfiles' % {'hp': get_setting('site','global','sitedisplayname')})
    link =  "/help-files/"
    description =  _("Latest Helpfiles by %(hp)s" % {'hp': get_setting('site','global','sitedisplayname')})

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
