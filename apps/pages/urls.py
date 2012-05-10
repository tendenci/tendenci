from django.conf.urls.defaults import patterns, url
from pages.feeds import LatestEntriesFeed

urlpatterns = patterns('',                  
    url(r'^$', 'pages.views.index', name="pages"),
    url(r'^search/$', 'pages.views.search', name="page.search"),
    url(r'^print-view/(?P<slug>[\w\-\/]+)/$', 'pages.views.print_view', name="page.print_view"),
    url(r'^export/$', 'pages.views.export', name="page.export"),
    url(r'^add/$', 'pages.views.add', name="page.add"),
    url(r'^edit/(?P<id>\d+)/$', 'pages.views.edit', name="page.edit"),
    url(r'^edit/meta/(?P<id>\d+)/$', 'pages.views.edit_meta', name="page.edit.meta"),
    url(r'^delete/(?P<id>\d+)/$', 'pages.views.delete', name="page.delete"),
    url(r'^feed/$', LatestEntriesFeed(), name='page.feed'),
)
