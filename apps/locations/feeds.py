from rss.feedsmanager import SubFeed
from site_settings.utils import get_setting
from perms.utils import PUBLIC_FILTER
from sitemaps import TendenciSitemap

from locations.models import Location

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest Locations' % get_setting('site','global','sitedisplayname')
    link =  "/locations/"
    description =  "Latest Locations by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        items = Location.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')[:20]
        return items

    def item_title(self, item):
        return item.location_name

    def item_description(self, item):
        return item.description

    def item_pubdate(self, item):
        return item.create_dt

    def item_link(self, item):
        return item.get_absolute_url()

class LocationSitemap(TendenciSitemap):
    """ Sitemap information for locations """
    changefreq = "yearly"
    priority = 0.3

    def items(self):
        items = Location(**PUBLIC_FILTER).order_by('-create_dt')
        return items

    def lastmod(self, obj):
        return obj.create_dt
