from rss.feedsmanager import SubFeed
from haystack.query import SearchQuerySet
from site_settings.utils import get_setting
from jobs.models import Job

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest Jobs' % get_setting('site','global','sitedisplayname')
    link =  "/jobs/"
    description =  "Latest Jobs by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        sqs = SearchQuerySet().filter(can_syndicate=True).models(Job).order_by('-create_dt')[:20]
        return [sq.object for sq in sqs]
    
    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description
