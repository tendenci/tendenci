from rss.feedsmanager import SubFeed
from haystack.query import SearchQuerySet

from models import ArchitectureProject
from sitemaps import TendenciSitemap

class LatestEntriesFeed(SubFeed):
    title =  'Latest Architecture Projects'
    link =  "/case-studies/"
    description =  "Latest Architecture Projects"

    def items(self):
        sqs = SearchQuerySet().models(ArchitectureProject).order_by('-create_dt')[:20]
        return [sq.object for sq in sqs]

    def item_title(self, item):
        return item.client

    def item_description(self, item):
        return item.overview

    def item_link(self, item):
        return item.get_absolute_url()


class ArchitectureProjectSitemap(TendenciSitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        sqs = SearchQuerySet().models(ArchitectureProject).order_by('-create_dt')
        return [sq.object for sq in sqs]

    def lastmod(self, obj):
        return obj.create_dt
