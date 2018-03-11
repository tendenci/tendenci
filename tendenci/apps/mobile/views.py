from django.shortcuts import redirect
from django.conf import settings

def toggle_mobile_mode(request):
    cookiename = getattr(settings, 'MOBILE_COOKIE_NAME', "tendenci_mobile")
    response = redirect(request.GET.get('next','/'))
    if request.mobile:
        response.set_cookie(cookiename, "0")
    else:
        response.set_cookie(cookiename, "1")
    return response
