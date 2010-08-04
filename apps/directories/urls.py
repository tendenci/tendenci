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
    url(r'^(?P<slug>[\w\-\/]+)/$', 'views.index', name="directory"),
)