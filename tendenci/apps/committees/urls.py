from django.conf.urls import url
from . import views
from .feeds import LatestEntriesFeed

urlpatterns = [
    url(r'^committees/$', views.search, name="committees.search"),
    url(r'^committees/add/$', views.add, name='committees.add'),
    url(r'^committees/edit/(?P<id>\d+)/$', views.edit, name='committees.edit'),
    url(r'^committees/edit/meta/(?P<id>\d+)/$', views.edit_meta, name="committees.edit.meta"),
    url(r'^committees/delete/(?P<id>\d+)/$', views.delete, name='committees.delete'),
    url(r'^committees/feed/$', LatestEntriesFeed(), name='committees.feed'),
    url(r'^committees/(?P<slug>[\w\-\/]+)/$', views.detail, name="committees.detail"),
]
