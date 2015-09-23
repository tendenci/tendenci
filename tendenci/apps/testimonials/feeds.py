from tendenci.apps.rss.feedsmanager import SubFeed
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.perms.utils import PUBLIC_FILTER
from tendenci.apps.sitemaps import TendenciSitemap

from tendenci.apps.testimonials.models import Testimonial

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest Testimonials' % get_setting('site','global','sitedisplayname')
    link =  "/testimonials/"
    description =  "Latest Testimonials %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        items = Testimonial.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')[:20]
        return items

    def item_title(self, item):
        return '%s, %s' % (item.first_name, item.last_name)

    def item_description(self, item):
        return item.testimonial

    def item_pubdate(self, item):
        return item.create_dt

    def item_link(self, item):
        return item.get_absolute_url()

class TestimonialSitemap(TendenciSitemap):
    """ Sitemap information for testimonials """
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        items = Testimonial.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')
        return items

    def lastmod(self, obj):
        return obj.create_dt
