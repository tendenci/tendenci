from django.shortcuts import redirect
from django.conf import settings
from tendenci.apps.base.utils import get_next_url

def toggle_mobile_mode(request):
    cookiename = getattr(settings, 'MOBILE_COOKIE_NAME', "tendenci_mobile")
    response = redirect(get_next_url(request) or '/')
    if request.mobile:
        response.set_cookie(cookiename, "0")
    else:
        response.set_cookie(cookiename, "1")
    return response
