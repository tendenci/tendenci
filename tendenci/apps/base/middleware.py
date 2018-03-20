from django.utils.deprecation import MiddlewareMixin

from tendenci.apps.base.http import Http403, render_to_403, MissingApp, render_to_missing_app


class Http403Middleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        from django.contrib.auth.views import redirect_to_login
        if isinstance(exception, Http403):
            if request.user.is_anonymous:
                return redirect_to_login(request.path)
            return render_to_403(request=request)


class MissingAppMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, MissingApp):
            return render_to_missing_app(request=request)
