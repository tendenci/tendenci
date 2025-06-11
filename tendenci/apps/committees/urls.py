from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed

urlpath = get_setting('module', 'committees', 'url') or 'committees'

urlpatterns = [
    re_path(fr'^{urlpath}/$', views.search, name="committees.search"),
    re_path(fr'^{urlpath}/add/$', views.add, name='committees.add'),
    re_path(fr'^{urlpath}/edit/(?P<id>\d+)/$', views.edit, name='committees.edit'),
    re_path(fr'^{urlpath}/edit/meta/(?P<id>\d+)/$', views.edit_meta, name="committees.edit.meta"),
    re_path(fr'^{urlpath}/delete/(?P<id>\d+)/$', views.delete, name='committees.delete'),
    re_path(fr'^{urlpath}/feed/$', LatestEntriesFeed(), name='committees.feed'),
    re_path(fr'^{urlpath}/(?P<slug>[\w\-\/]+)/$', views.detail, name="committees.detail"),
]
