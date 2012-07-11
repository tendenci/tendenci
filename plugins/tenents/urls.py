from django.conf.urls.defaults import patterns, url
from tenents.feeds import LatestEntriesFeed

urlpatterns = patterns('tenents.views',
    url(r'^maps/$', 'tenents_maps', name="tenents.maps"),
    url(r'^maps/tenents/$', 'tenents', name='tenents'),
    url(r'^maps/add/$', 'tenents_maps_add', name="tenents.maps.add"),
    url(r'^maps/tenents/edit/(?P<pk>[\d/]+)/$', 'tenents_edit', name="tenents.edit"),
    url(r'^maps/tenents/delete/(?P<pk>[\d/]+)/$', 'tenents_delete', name="tenents.delete"),
    url(r'^maps/tenents/add/(?P<pk>[\d/]+)/$', 'tenents_add', name="tenents.add"),
    url(r'^maps/edit/(?P<pk>[\d/]+)/$', 'tenents_maps_edit', name="tenents.maps.edit"),
    url(r'^maps/delete/(?P<pk>[\d/]+)/$', 'tenents_maps_delete', name="tenents.maps.delete"),
    url(r'^maps/feed/$', LatestEntriesFeed(), name='tenents.maps.feed'),

    url(r'^maps/tenents/kinds/$', 'tenents_kinds', name="tenents.kinds"),
    url(r'^maps/tenents/kinds/(?P<pk>[\d/]+)/$', 'tenents_kinds_detail', name="tenents.kinds.detail"),
    url(r'^maps/tenents/kinds/add/$', 'tenents_kinds_add', name="tenents.kinds.add"),
    url(r'^maps/tenents/kinds/edit/(?P<pk>[\d/]+)/$', 'tenents_kinds_edit', name="tenents.kinds.edit"),
    url(r'^maps/tenents/kinds/delete/(?P<pk>[\d/]+)/$', 'tenents_kinds_delete', name="tenents.kinds.delete"),

    url(r'^maps/tenents/(?P<slug>[\w\-\/]+)/$', 'tenents_detail', name="tenents"),
    url(r'^maps/(?P<slug>[\w\-\/]+)/$', 'tenents_maps_detail', name="tenents.maps"),
)
