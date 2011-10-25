from django.conf.urls.defaults import *

from piston.resource import Resource

from api_piston.handlers import SettingHandler

setting_handler = Resource(SettingHandler)

urlpatterns = patterns('',
    url(r'^setting/(?P<setting_id>\d+)/$', setting_handler),
    url(r'^settings/$', setting_handler),
)
