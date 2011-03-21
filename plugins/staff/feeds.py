from rss.feedsmanager import SubFeed
from haystack.query import SearchQuerySet

from models import Staff
from sitemaps import TendenciSitemap

class LatestEntriesFeed(SubFeed):
    title =  'Latest Staff'
    link =  "/staff/"
    description =  "Latest Staff"

    def items(self):
        sqs = SearchQuerySet().models(Staff).order_by('-start_dt')[:20]
        return [sq.object for sq in sqs]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.biography

    def item_link(self, item):
        return item.get_absolute_url()

class StaffSitemap(TendenciSitemap):
    changefreq = "monthly"
    priority = 0.5
    
    def items(self):
        sqs = SearchQuerySet().models(Staff).order_by('-start_dt')
        return [sq.object for sq in sqs]
    
    def lastmod(self, obj):
        return obj.start_dt
