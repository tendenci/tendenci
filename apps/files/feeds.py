#import mimetypes
from django.contrib.syndication.views import Feed
#from django.core.urlresolvers import reverse

from site_settings.utils import get_setting
from files.models import File

class LatestEntriesFeed(Feed):
    title =  '%s Latest Files' % get_setting('site','global','sitedisplayname')
    link =  "/files/"
    description =  "Latest Files by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        return File.objects.order_by('-create_dt')[:20]
    
    def item_title(self, item):
        return item.basename()

    def item_description(self, item):
        return item.description

#    def item_enclosure_url(self, item):
#        return reverse('file', args=[item.pk])
#
#    def item_enclosure_length(self, item):
#        return item.file.size
#
#    def item_enclosure_mime_type(self, item):
#
#        types = { # list of uncommon mimetypes
#            'application/msword': ('.doc','.docx'),
#            'application/ms-powerpoint': ('.ppt','.pptx'),
#            'application/ms-excel': ('.xls','.xlsx'),
#            'video/x-ms-wmv': ('.wmv',),
#        }
#        # add mimetypes
#        for type in types:
#            for ext in types[type]:
#                mimetypes.add_type(type, ext)
#    
#        mimetype = mimetypes.guess_type(item.file.name)[0]
#        return mimetype