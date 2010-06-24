#import sys
#import tempfile
#import hotshot.stats
#from cStringIO import StringIO

#from django.conf import settings
from django.template import RequestContext
from django.conf import settings
from django.core.exceptions import PermissionDenied

from base.http import Http403, render_to_403

class Http403Middleware(object):
    def process_exception(self,request,exception):
        if isinstance(exception,Http403):
            if settings.DEBUG:
                raise PermissionDenied
            return render_to_403(context_instance=RequestContext(request))     

#class ProfileMiddleware(object):
#    """
#    Displays hotshot profiling for any view.
#    http://yoursite.com/yourview/?prof
#
#    Add the "prof" key to query string by appending ?prof (or &prof=)
#    and you'll see the profiling results in your browser.
#    It's set up to only be available in django's debug mode,
#    but you really shouldn't add this middleware to any production configuration.
#    * Only tested on Linux
#    """
#    def process_request(self, request):
#        if settings.DEBUG and request.GET.has_key('prof'):
#            self.tmpfile = tempfile.NamedTemporaryFile(delete=False)
#            self.prof = hotshot.Profile(self.tmpfile.name)
#
#    def process_view(self, request, callback, callback_args, callback_kwargs):
#        if settings.DEBUG and request.GET.has_key('prof'):
#            return self.prof.runcall(callback, request, *callback_args, **callback_kwargs)
#
#    def process_response(self, request, response):
#        if settings.DEBUG and request.GET.has_key('prof'):
#            self.prof.close()
#
#            out = StringIO()
#            old_stdout = sys.stdout
#            sys.stdout = out
#
#            stats = hotshot.stats.load(self.tmpfile.name)
#            #stats.strip_dirs()
#            stats.sort_stats('time', 'calls')
#            stats.print_stats()
#
#            sys.stdout = old_stdout
#            stats_str = out.getvalue()
#
#            if response and response.content and stats_str:
#                response.content = "<pre>" + stats_str + "</pre>"
#
#        return response