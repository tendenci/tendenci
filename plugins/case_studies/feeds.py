from rss.feedsmanager import SubFeed
from haystack.query import SearchQuerySet

from models import CaseStudy
from sitemaps import TendenciSitemap

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


class CaseStudySitemap(TendenciSitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        sqs = SearchQuerySet().models(CaseStudy).order_by('-create_dt')
        return [sq.object for sq in sqs]

    def lastmod(self, obj):
        return obj.create_dt
