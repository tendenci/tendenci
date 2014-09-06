from django.template import RequestContext

from tendenci.apps.base.http import Http403, render_to_403, MissingApp, render_to_missing_app


class Http403Middleware(object):
    def process_exception(self, request, exception):
        from django.contrib.auth.views import redirect_to_login
        if isinstance(exception, Http403):
            if request.user.is_anonymous():
                return redirect_to_login(request.path)
            return render_to_403(context_instance=RequestContext(request))


class MissingAppMiddleware(object):
    def process_exception(self, request, exception):
        if isinstance(exception, MissingApp):
            return render_to_missing_app(context_instance=RequestContext(request))
