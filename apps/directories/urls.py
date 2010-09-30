from django.conf.urls.defaults import patterns, url
from directories.feeds import LatestEntriesFeed

urlpatterns = patterns('directories',                  
    url(r'^$', 'views.index', name="directories"),
    url(r'^search/$', 'views.search', name="directory.search"),
    url(r'^print-view/(?P<slug>[\w\-\/]+)/$', 'views.print_view', name="directory.print_view"),
    url(r'^add/$', 'views.add', name="directory.add"),
    url(r'^edit/(?P<id>\d+)/$', 'views.edit', name="directory.edit"),
    url(r'^edit/meta/(?P<id>\d+)/$', 'views.edit_meta', name="directory.edit.meta"),
    url(r'^delete/(?P<id>\d+)/$', 'views.delete', name="directory.delete"),
    url(r'^feed/$', LatestEntriesFeed(), name='directory.feed'),
    url(r'^pricing/(?P<id>\d+)/$', 'views.pricing_view', name="directory_pricing.view"),
    url(r'^pricing/add/$', 'views.pricing_add', name="directory_pricing.add"),
    url(r'^pricing/edit/(?P<id>\d+)/$', 'views.pricing_edit', name="directory_pricing.edit"),
    url(r'^pricing/delete/(?P<id>\d+)/$', 'views.pricing_delete', name="directory_pricing.delete"),
    url(r'^pricing/search/$', 'views.pricing_search', name="directory_pricing.search"),
    url(r'^(?P<slug>[\w\-\/]+)/$', 'views.index', name="directory"),
)