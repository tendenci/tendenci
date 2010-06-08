from django.contrib.syndication.views import Feed

from site_settings.utils import get_setting
from pages.models import Page

class LatestEntriesFeed(Feed):
    title =  '%s Latest News' % get_setting('site','global','sitedisplayname')
    link =  "/news/"
    description =  "Latest News by %s" % get_setting('site','global','sitedisplayname')

    title_template = 'feeds/page_title.html'
    description_template = 'feeds/page_description.html'

    def items(self):
        return Page.objects.order_by('-create_dt')[:20]
    
#    def item_title(self, item):
#        return item.title
#
#    def item_description(self, item):
#        return item.content