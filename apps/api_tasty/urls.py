from django.conf.urls.defaults import *

from api_tasty.api import SettingResource

setting_resource = SettingResource()

urlpatterns = patterns('',
    (r'^', include(setting_resource.urls)),
)
