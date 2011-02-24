from rss.feedsmanager import SubFeed

from site_settings.utils import get_setting
from contacts.models import Contact

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest Contacts' % get_setting('site','global','sitedisplayname')
    link =  "/contacts/"
    description =  "Latest Contacts by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        return Contact.objects.order_by('-create_dt')[:20]
    
    def item_title(self, item):
        return '%s %s' % (item.first_name, item.last_name)

    def item_description(self, item):
        return item.message
