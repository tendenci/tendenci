from django.template import RequestContext
from django.shortcuts import redirect
from django.conf import settings

def toggle_mobile_mode(request, redirect_url):
    cookiename = getattr(settings, 'MOBILE_COOKIE_NAME', "tendenci_mobile")
    response = redirect(redirect_url)
    if request.mobile:
        response.set_cookie(cookiename, "0")
    else:
        response.set_cookie(cookiename, "1")
    return response
