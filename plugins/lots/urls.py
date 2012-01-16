from django.conf.urls.defaults import patterns, url
from lots.feeds import LatestEntriesFeed

urlpatterns = patterns('lots.views',                  
    url(r'^lots/$', 'index', name="lots"),
    url(r'^lots/search/$', 'search', name="lots.search"),
    url(r'^lots/feed/$', LatestEntriesFeed(), name='lots.feed'),
    url(r'^lots/(?P<pk>[\d/]+)/$', 'detail', name="lots.detail"),
)