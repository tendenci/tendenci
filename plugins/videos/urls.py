from django.conf.urls.defaults import *

urlpatterns = patterns('plugins.videos.views',
    url(r'^videos/$', 'index', name="video"),
    url(r'^videos/category/([^/]+)/$', 'index', name="video-category"),
    url(r'^videos/search/$', 'search', name="video-search"),
    url(r'^videos/([^/]+)/$', 'details', name="video-details"),
)