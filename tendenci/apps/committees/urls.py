from django.urls import path, re_path
from . import views
from .feeds import LatestEntriesFeed

urlpatterns = [
    re_path(r'^committees/$', views.search, name="committees.search"),
    re_path(r'^committees/add/$', views.add, name='committees.add'),
    re_path(r'^committees/edit/(?P<id>\d+)/$', views.edit, name='committees.edit'),
    re_path(r'^committees/edit/meta/(?P<id>\d+)/$', views.edit_meta, name="committees.edit.meta"),
    re_path(r'^committees/delete/(?P<id>\d+)/$', views.delete, name='committees.delete'),
    re_path(r'^committees/feed/$', LatestEntriesFeed(), name='committees.feed'),
    re_path(r'^committees/(?P<slug>[\w\-\/]+)/$', views.detail, name="committees.detail"),
]
