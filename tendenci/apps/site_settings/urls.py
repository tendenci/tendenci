from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name="settings"),
    url(r'^(?P<scope>\w+)/(?P<scope_category>\w+)/$', views.list, name="settings.index"),
    url(r'^(?P<scope>\w+)/(?P<scope_category>\w+)/(?P<name>\w+)/$', views.single_setting, name="settings.single_setting"),
    #url(r'^(?P<scope>\w+)/(?P<scope_category>\w+)/([#\w]+)$', views.list, name="setting.permalink"),
    url(r'^(?P<scope>\w+)/(?P<scope_category>\w+)/#id_(\w+)$', views.list, name="setting.permalink"),
]
