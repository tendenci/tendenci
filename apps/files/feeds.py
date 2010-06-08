import mimetypes
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse

from site_settings.utils import get_setting
from files.models import File

class LatestEntriesFeed(Feed):
    title =  '%s Latest Files' % get_setting('site','global','sitedisplayname')
    link =  "/files/"
    description =  "Latest Files by %s" % get_setting('site','global','sitedisplayname')

    description_template = 'feeds/file_description.html'

    def items(self):
        return File.objects.order_by('-create_dt')[:50]
    
    def item_title(self, item):
        return item.basename()
#
    def item_description(self, item):
        return item.description

    def item_enclosure_url(self, item): # TODO: replace w/ get_absolute_url; when method is good (again)
        return '%s%s' % (get_setting('site','global','siteurl'), reverse('file', args=[item.pk]))

    def item_enclosure_length(self, item):
        # try. incase image is lost/
        try: return item.file.size
        except: return 0 # 0 bytes

    def item_enclosure_mime_type(self, item):
        return item.mime_type()