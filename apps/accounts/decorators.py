from site_settings.models import Setting
from functools import wraps
from django.conf import settings

# looks like this is not being used anywhere
def fb_wrapper(func):
    def decorator(*args, **kwargs):
        try:
            settings.FACEBOOK_API_KEY = Setting.objects.get(name='facebook_api_key').get_value()
            settings.FACEBOOK_APP_ID = Setting.objects.get(name='facebook_app_id').get_value()
            settings.FACEBOOK_APP_SECRET = Setting.objects.get(name='facebook_app_secret').get_value()
        except Setting.DoesNotExist:
            raise Http404("Facebook API variables not specified")
        return func(*args, **kwargs)
    return decorator
