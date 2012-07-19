from django.conf import settings
from django.http import HttpResponseRedirect

def ssl_required(view_func):
    """Decorator to force url to be accessed over SSL (https).
    """
    def decorator(request, *args, **kwargs):
        if not request.is_secure():
            if getattr(settings, 'SSL_ENABLED', False):
                request_url = request.build_absolute_uri(request.get_full_path())
                ssl_url = request_url.replace('http://', 'https://')
                return HttpResponseRedirect(ssl_url)
        return view_func(request, *args, **kwargs)
    return decorator