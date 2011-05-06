from site_settings.models import Setting
from functools import wraps
from django.conf import settings

def fb_wrapper(func):
    def decorator(*args, **kwargs):
        try:
            settings.FACEBOOK_API_KEY = Setting.objects.get(name='facebook_api_key').value
            settings.FACEBOOK_APP_ID = Setting.objects.get(name='facebook_app_id').value
            settings.FACEBOOK_APP_SECRET = Setting.objects.get(name='facebook_app_secret').value
        except Setting.DoesNotExist:
            raise Http404("Facebook API variables not specified")
        return func(*args, **kwargs)
    return decorator
