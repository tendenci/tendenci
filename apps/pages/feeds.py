from rss.feedsmanager import SubFeed
from haystack.query import SearchQuerySet
from site_settings.utils import get_setting
from pages.models import Page

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest News' % get_setting('site','global','sitedisplayname')
    link =  "/news/"
    description =  "Latest News by %s" % get_setting('site','global','sitedisplayname')

    title_template = 'feeds/page_title.html'
    description_template = 'feeds/page_description.html'

    def items(self):
        sqs = SearchQuerySet().filter(can_syndicate=True).models(Page).order_by('-create_dt')[:20]
        return [sq.object for sq in sqs]
    
    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content
