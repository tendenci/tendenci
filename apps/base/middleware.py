from django.template import RequestContext
from django.conf import settings
from django.core.exceptions import PermissionDenied

from base.http import Http403, render_to_403

class Http403Middleware(object):
    def process_exception(self, request, exception):
        from django.contrib.auth.views import redirect_to_login
        if isinstance(exception, Http403):
            if request.user.is_anonymous():
                return redirect_to_login(request.path)
            return render_to_403(context_instance=RequestContext(request))