from django.conf.urls.defaults import *

from api_tasty.api import (SafeApi, SettingResource, UserResource,
    ProfileResource, DiscountResource)

api = SafeApi(api_name='v1')
api.register(UserResource())
api.register(ProfileResource())
api.register(SettingResource())
api.register(DiscountResource())

urlpatterns = patterns('',
    (r'^', include(api.urls)),
)
