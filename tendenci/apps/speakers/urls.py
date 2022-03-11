from django.urls import path, re_path
from . import views
from .feeds import LatestEntriesFeed

urlpatterns = [
    re_path(r'^speakers/$', views.search, name="speakers"),
    re_path(r'^speakers/search/$', views.search_redirect, name="speaker.search"),
    re_path(r'^speakers/feed/$', LatestEntriesFeed(), name='speaker.feed'),
    re_path(r'^speakers/(?P<slug>[\w\-]+)/$', views.details, name="speaker.view"),
]
