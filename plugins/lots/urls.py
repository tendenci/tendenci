from django.conf.urls.defaults import patterns, url
from lots.feeds import LatestEntriesFeed

urlpatterns = patterns('lots.views',                  
    url(r'^lots/$', 'index', name="lots"),
    url(r'^lots/maps/$', 'map_selection', name='lots.map_selection'),
    url(r'^lots/maps/add/$', 'map_add', name="lots.map_add"),
    url(r'^lots/maps/(?P<pk>[\d/]+)/$', 'map_detail', name="lots.map_detail"),
    url(r'^lots/add/$', 'add', name="lots.add"),
    url(r'^lots/add/(?P<map_id>[\d/]+)/$', 'add', name="lots.add"),
    url(r'^lots/edit/(?P<pk>[\d/]+)/$', 'edit', name="lots.edit"),
    url(r'^lots/search/$', 'search', name="lots.search"),
    url(r'^lots/feed/$', LatestEntriesFeed(), name='lots.feed'),
    url(r'^lots/(?P<pk>[\d/]+)/$', 'detail', name="lots.detail"),
)
