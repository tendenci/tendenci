import time
import re
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.http import urlquote
from django.shortcuts import redirect

PASSWORD_PROMT_MAX_AGE = 30 * 60      # 30 minites


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


def password_required(view):
    """Decorator to force a password promt"""
    def decorator(request, *args, **kwargs):
        if settings.PASSWORD_UNUSABLE:
            # Since users cannot log in to the site directly, there is
            # no password can be entered.
            # Why don't we force them to log in again? Because
            # @password_required always comes after the @login_required,
            # at this point, user is already logged in. In order to 
            # redirect them back to IdP, we'd need to log them out first,
            # which would lead to an infinite loop. 
            return view(request, *args, **kwargs)
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


def strip_control_chars(func):
    """
    This decorater can be used to strip control chars from RSS feeds to avoid the
    UnserializableContentError because control characters are not supported in XML 1.0.
    """
    def wrapper(self, obj):
        result = func(self, obj)
        return re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', result)
    return wrapper
