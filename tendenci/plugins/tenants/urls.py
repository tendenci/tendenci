from django.conf.urls.defaults import patterns, url
from tenants.feeds import LatestEntriesFeed

urlpatterns = patterns('tenants.views',
    url(r'^maps/$', 'tenants_maps', name="tenants.maps"),
    url(r'^maps/tenants/$', 'tenants', name='tenants'),
    url(r'^maps/add/$', 'tenants_maps_add', name="tenants.maps.add"),
    url(r'^maps/tenants/edit/(?P<pk>[\d/]+)/$', 'tenants_edit', name="tenants.edit"),
    url(r'^maps/tenants/delete/(?P<pk>[\d/]+)/$', 'tenants_delete', name="tenants.delete"),
    url(r'^maps/tenants/add/(?P<pk>[\d/]+)/$', 'tenants_add', name="tenants.add"),
    url(r'^maps/edit/(?P<pk>[\d/]+)/$', 'tenants_maps_edit', name="tenants.maps.edit"),
    url(r'^maps/delete/(?P<pk>[\d/]+)/$', 'tenants_maps_delete', name="tenants.maps.delete"),
    url(r'^maps/feed/$', LatestEntriesFeed(), name='tenants.maps.feed'),

    url(r'^maps/tenants/kinds/$', 'tenants_kinds', name="tenants.kinds"),
    url(r'^maps/tenants/kinds/(?P<pk>[\d/]+)/$', 'tenants_kinds_detail', name="tenants.kinds.detail"),
    url(r'^maps/tenants/kinds/add/$', 'tenants_kinds_add', name="tenants.kinds.add"),
    url(r'^maps/tenants/kinds/edit/(?P<pk>[\d/]+)/$', 'tenants_kinds_edit', name="tenants.kinds.edit"),
    url(r'^maps/tenants/kinds/delete/(?P<pk>[\d/]+)/$', 'tenants_kinds_delete', name="tenants.kinds.delete"),

    url(r'^maps/tenants/(?P<slug>[\w\-\/]+)/$', 'tenants_detail', name="tenants"),
    url(r'^maps/(?P<slug>[\w\-\/]+)/$', 'tenants_maps_detail', name="tenants.maps"),
)
