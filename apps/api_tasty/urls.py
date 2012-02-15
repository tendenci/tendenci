from django.conf.urls.defaults import *

from api_tasty.api import (SafeApi, SettingResource, UserResource,
    ProfileResource, DiscountResource, EntityResource)

api = SafeApi(api_name='v1')
api.register(UserResource())
api.register(EntityResource())
api.register(ProfileResource())
api.register(SettingResource())
api.register(DiscountResource())

urlpatterns = patterns('',
    (r'^', include(api.urls)),
)
