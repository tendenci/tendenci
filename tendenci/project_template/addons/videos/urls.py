from django.conf.urls.defaults import *
from addons.videos.feeds import LatestEntriesFeed

urlpatterns = patterns('addons.videos.views',
    url(r'^videos/$', 'search', name="video"),
    url(r'^videos/category/([^/]+)/$', 'index', name="video.category"),
    url(r'^videos/search/$', 'search', name="video.search"),
    url(r'^videos/feed/$', LatestEntriesFeed(), name='video.feed'),
    url(r'^videos/([^/]+)/$', 'detail', name="video.details"),
)