from rss.feedsmanager import SubFeed
from haystack.query import SearchQuerySet

from models import Video
from sitemaps import TendenciSitemap

class LatestEntriesFeed(SubFeed):
    title =  'Latest Videos'
    link =  "/videos/"
    description =  "Latest Videos"

    def items(self):
        sqs = SearchQuerySet().models(Video).order_by('-create_dt')[:20]
        return [sq.object for sq in sqs]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.embed_code()+item.description

    def item_link(self, item):
        return item.get_absolute_url()


class VideoSitemap(TendenciSitemap):
    changefreq = "monthly"
    priority = 0.5
    
    def items(self):
        sqs = SearchQuerySet().models(Video).order_by('-create_dt')
        return [sq.object for sq in sqs]
                                        
    def lastmod(self, obj):
        return obj.create_dt
    
