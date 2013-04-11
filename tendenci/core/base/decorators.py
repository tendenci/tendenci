import time
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.http import urlquote
from django.shortcuts import redirect

PASSWORD_PROMT_MAX_AGE = 30 * 60      # 30 minites


def ssl_required(view_func):
    """Decorator to force url to be accessed over SSL (https).
    """
    def decorator(request, *args, **kwargs):
        if not any([request.is_secure(), request.META.get("HTTP_X_FORWARDED_PROTO", "") == 'https']):
            if getattr(settings, 'SSL_ENABLED', False):
                request_url = request.build_absolute_uri(request.get_full_path())
                ssl_url = request_url.replace('http://', 'https://')
                return HttpResponseRedirect(ssl_url)
        return view_func(request, *args, **kwargs)
    return decorator


def password_required(view):
    """Decorator to force a password promt"""
    def decorator(request, *args, **kwargs):
        if 'password_promt' in request.session and \
            isinstance(request.session['password_promt'], dict) and \
            request.session['password_promt'].get('value', False):
            tstart = request.session['password_promt'].get('time', 0)
            pwd_age = int(time.time()) - tstart
            if pwd_age < PASSWORD_PROMT_MAX_AGE:
                return view(request, *args, **kwargs)
        return redirect(("%s?next=%s") % (reverse("password_again"),
                                          urlquote(request.get_full_path())))
    return decorator
