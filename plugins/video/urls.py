from django.conf.urls.defaults import *

urlpatterns = patterns('plugins.video.views',
    url(r'^video/$', 'index', name="video"),
    url(r'^video/category/([^/]+)/$', 'index', name="video-category"),
    url(r'^video/search/$', 'search', name="video-search"),
    url(r'^video/([^/]+)/$', 'details', name="video-details"),
)