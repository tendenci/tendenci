from django.contrib.syndication.views import Feed

from site_settings.utils import get_setting
from jobs.models import Job

class LatestEntriesFeed(Feed):
    title =  '%s Latest Jobs' % get_setting('site','global','sitedisplayname')
    link =  "/jobs/"
    description =  "Latest Jobs by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        return Job.objects.order_by('-create_dt')[:20]
    
    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description