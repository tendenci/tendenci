from rss.feedsmanager import SubFeed
from haystack.query import SearchQuerySet

from models import Testimonial
from sitemaps import TendenciSitemap

class LatestEntriesFeed(SubFeed):
    title =  'Latest Testimonials'
    link =  "/testimonials/"
    description =  "Latest Testimonials"

    def items(self):
        sqs = SearchQuerySet().models(Testimonial).order_by('-create_dt')[:20]
        return [sq.object for sq in sqs]

    def item_title(self, item):
        return '%s, %s' % (item.first_name, item.last_name)

    def item_description(self, item):
        return item.testimonial

    def item_link(self, item):
        return item.get_absolute_url()


class TestimonialSitemap(TendenciSitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        sqs = SearchQuerySet().models(Testimonial).order_by('-create_dt')
        return [sq.object for sq in sqs]

    def lastmod(self, obj):
        return obj.create_dt
    
