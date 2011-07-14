from rss.feedsmanager import SubFeed
from haystack.query import SearchQuerySet

from models import Speaker
from sitemaps import TendenciSitemap

class LatestEntriesFeed(SubFeed):
    title =  'Latest Speaker'
    link =  "/speakers/"
    description =  "Latest Speaker"

    def items(self):
        sqs = SearchQuerySet().models(Speaker).order_by('ordering')[:20]
        return [sq.object for sq in sqs]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.biography

    def item_link(self, item):
        return item.get_absolute_url()

class SpeakerSitemap(TendenciSitemap):
    changefreq = "monthly"
    priority = 0.5
    
    def items(self):
        sqs = SearchQuerySet().models(Speaker).order_by('-start_dt')
        return [sq.object for sq in sqs]
    
    def lastmod(self, obj):
        return obj.update_dt
