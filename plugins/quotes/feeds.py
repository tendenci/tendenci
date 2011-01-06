from django.contrib.syndication.views import Feed
from haystack.query import SearchQuerySet

from site_settings.utils import get_setting
from quotes.models import Quote

class LatestEntriesFeed(Feed):
    title =  '%s Latest Quotes' % get_setting('site','global','sitedisplayname')
    link =  "/quotes/"
    description =  "Latest Quotes by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        sqs = SearchQuerySet().filter(can_syndicate=True).models(Quote).order_by('-create_dt')[:20]
        return [sq.object for sq in sqs]

    def item_title(self, item):
        return item.author

    def item_description(self, item):
        return item.quote