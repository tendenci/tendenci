from site_settings.models import Setting
from functools import wraps
from django.conf import settings

def fb_init():
    def decorator(func):
        def inner_decorator(request, *args, **kwargs):
            try:
                settings.FACEBOOK_API_KEY = Setting.objects.get(name='facebook_api_key')
                settings.FACEBOOK_API_ID = Setting.objects.get(name='facebook_api_id')
                settings.FACEBOOK_API_SECRET = Setting.objects.get(name='facebook_api_secret')
            except Setting.DoesNotExist:
                raise Http404("Facebook API variables not specified")
            return func(request, *args, **kwargs)
        return wraps(func)(inner_decorator)
    return decorator
