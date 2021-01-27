from django.conf.urls import url
from . import views
from .feeds import LatestEntriesFeed

urlpatterns = [
    url(r'^chapters/$', views.search, name="chapters.search"),
    url(r'^chapters/add/$', views.add, name='chapters.add'),
    url(r'^chapters/edit/(?P<id>\d+)/$', views.edit, name='chapters.edit'),
    url(r'^chapters/edit/meta/(?P<id>\d+)/$', views.edit_meta, name="chapters.edit.meta"),
    url(r'^chapters/delete/(?P<id>\d+)/$', views.delete, name='chapters.delete'),
    url(r'^chapters/feed/$', LatestEntriesFeed(), name='chapters.feed'),
    url(r'^chapters/(?P<slug>[\w\-\/]+)/$', views.detail, name="chapters.detail"),
]
