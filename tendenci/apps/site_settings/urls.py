from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.index, name="settings"),
    re_path(r'^(?P<scope>\w+)/(?P<scope_category>\w+)/$', views.list, name="settings.index"),
    re_path(r'^(?P<scope>\w+)/(?P<scope_category>\w+)/(?P<name>\w+)/$', views.single_setting, name="settings.single_setting"),
    #re_path(r'^(?P<scope>\w+)/(?P<scope_category>\w+)/([#\w]+)$', views.list, name="setting.permalink"),
    re_path(r'^(?P<scope>\w+)/(?P<scope_category>\w+)/#id_(\w+)$', views.list, name="setting.permalink"),
]
