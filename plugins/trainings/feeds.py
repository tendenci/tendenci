from rss.feedsmanager import SubFeed
from haystack.query import SearchQuerySet

from site_settings.utils import get_setting
from trainings.models import Training
from sitemaps import TendenciSitemap

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest Trainings' % get_setting('site','global','sitedisplayname')
    link =  "/trainings/"
    description =  "Latest Trainings by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        sqs = SearchQuerySet().filter(can_syndicate=True).models(Training).order_by('-create_dt')[:20]
        return [sq.object for sq in sqs]

    def item_title(self, item):
        return item.author

    def item_description(self, item):
        return item.training

    def item_link(self, item):
        return item.get_absolute_url()

class TrainingSitemap(TendenciSitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        sqs = SearchQuerySet().models(Training).order_by('-create_dt')
        return [sq.object for sq in sqs]

    def lastmod(self, obj):
        return obj.create_dt
    