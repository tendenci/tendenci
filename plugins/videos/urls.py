from django.conf.urls.defaults import *
from feeds import LatestEntriesFeed

urlpatterns = patterns('plugins.videos.views',
    url(r'^videos/$', 'index', name="video"),
    url(r'^videos/category/([^/]+)/$', 'index', name="video.category"),
    url(r'^videos/search/$', 'search', name="video.search"),
    url(r'^videos/feed/$', LatestEntriesFeed(), name='video.feed'),
    url(r'^videos/([^/]+)/$', 'details', name="video.details"),
)