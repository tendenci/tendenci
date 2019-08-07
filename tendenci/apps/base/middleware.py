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


class RemoveNullByteMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Remove Null Byte to avoid Null Byte Injection attack
        request.GET._mutable = True
        null_byte = chr(0)
        if request.method == 'GET' and null_byte in request.GET.values():
            for k in request.GET:
                request.GET[k] = request.GET[k].replace(null_byte, '')
        request.GET._mutable = False