from django.conf.urls.defaults import patterns, url
from plugs.feeds import LatestEntriesFeed

urlpatterns = patterns('plugs.views',                  
    url(r'^plugs/$', 'index', name="plugs"),
    url(r'^plugs/search/$', 'search', name="plugs.search"),
    url(r'^plugs/feed/$', LatestEntriesFeed(), name='plugs.feed'),
    url(r'^plugs/(?P<pk>[\d/]+)/$', 'detail', name="plugs.detail"),
)