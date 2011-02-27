from rss.feedsmanager import SubFeed
from haystack.query import SearchQuerySet

from models import CaseStudy

class LatestEntriesFeed(SubFeed):
    title =  'Latest Case Studies'
    link =  "/case-studies/"
    description =  "Latest Case Studies"

    def items(self):
        sqs = SearchQuerySet().models(CaseStudy).order_by('-create_dt')[:20]
        return [sq.object for sq in sqs]

    def item_title(self, item):
        return item.client

    def item_description(self, item):
        return item.overview

    def item_link(self, item):
        return item.get_absolute_url()
