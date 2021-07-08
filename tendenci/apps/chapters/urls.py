from django.urls import path, re_path
from . import views
from .feeds import LatestEntriesFeed

urlpatterns = [
    re_path(r'^chapters/$', views.search, name="chapters.search"),
    re_path(r'^chapters/add/$', views.add, name='chapters.add'),
    re_path(r'^chapters/edit/(?P<id>\d+)/$', views.edit, name='chapters.edit'),
    re_path(r'^chapters/edit/meta/(?P<id>\d+)/$', views.edit_meta, name="chapters.edit.meta"),
    re_path(r'^chapters/delete/(?P<id>\d+)/$', views.delete, name='chapters.delete'),
    re_path(r'^chapters/feed/$', LatestEntriesFeed(), name='chapters.feed'),
    re_path(r'^chapters/(?P<slug>[\w\-\/]+)/$', views.detail, name="chapters.detail"),
]
