from rss.feedsmanager import SubFeed
from haystack.query import SearchQuerySet

from models import Video

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
