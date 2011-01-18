from django.contrib.syndication.views import Feed
from haystack.query import SearchQuerySet

from models import CaseStudy

class LatestEntriesFeed(Feed):
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