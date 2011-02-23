from rss.feedsmanager import SubFeed

from site_settings.utils import get_setting
from resumes.models import Resume

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest Resumes' % get_setting('site','global','sitedisplayname')
    link =  "/resumes/"
    description =  "Latest Resumes by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        return Resume.objects.order_by('-create_dt')[:20]
    
    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description
