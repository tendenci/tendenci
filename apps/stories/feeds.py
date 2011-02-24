from rss.feedsmanager import SubFeed
from haystack.query import SearchQuerySet
from site_settings.utils import get_setting
from stories.models import Story

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest Stories' % get_setting('site','global','sitedisplayname')
    link =  "/stories/"
    description =  "Latest Stories by %s" % get_setting('site','global','sitedisplayname')

    title_template = 'feeds/story_title.html'
    description_template = 'feeds/story_description.html'

    def items(self):
        sqs = SearchQuerySet().filter(can_syndicate=True).models(Story).order_by('-create_dt')[:20]
        return [sq.object for sq in sqs]
    
    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content
