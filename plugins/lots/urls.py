from django.conf.urls.defaults import patterns, url
from lots.feeds import LatestEntriesFeed

urlpatterns = patterns('lots.views',
    url(r'^lots/$', 'index', name="lots"),
    url(r'^lots/maps/$', 'map_selection', name='lots.map_selection'),
    url(r'^lots/maps/add/$', 'map_add', name="lots.map_add"),
    url(r'^lots/maps/edit/(?P<pk>[\d/]+)/$', 'map_edit', name="lots.map_edit"),
    url(r'^lots/maps/delete/(?P<pk>[\d/]+)/$', 'map_delete', name="lots.map_delete"),
    url(r'^lots/maps/(?P<pk>[\d/]+)/$', 'map_detail', name="lots.map_detail"),
    url(r'^lots/add/(?P<pk>[\d/]+)/$', 'add', name="lots.add"),
    url(r'^lots/edit/(?P<pk>[\d/]+)/$', 'edit', name="lots.edit"),
    url(r'^lots/delete/(?P<pk>[\d/]+)/$', 'delete', name="lots.delete"),
    url(r'^lots/search/$', 'search', name="lots.search"),
    url(r'^lots/feed/$', LatestEntriesFeed(), name='lots.feed'),
    url(r'^lots/(?P<pk>[\d/]+)/$', 'detail', name="lots.detail"),
)
