from rss.feedsmanager import SubFeed
from haystack.query import SearchQuerySet

from models import Testimonial

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
