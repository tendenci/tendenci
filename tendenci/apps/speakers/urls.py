from django.conf.urls import url
from . import views
from .feeds import LatestEntriesFeed

urlpatterns = [
    url(r'^speakers/$', views.search, name="speakers"),
    url(r'^speakers/search/$', views.search_redirect, name="speaker.search"),
    url(r'^speakers/feed/$', LatestEntriesFeed(), name='speaker.feed'),
    url(r'^speakers/(?P<slug>[\w\-]+)/$', views.details, name="speaker.view"),
]
