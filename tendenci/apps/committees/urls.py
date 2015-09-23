from django.conf.urls import patterns, url
from tendenci.apps.committees.feeds import LatestEntriesFeed

urlpatterns = patterns('tendenci.apps.committees.views',
    url(r'^committees/$', 'search', name="committees.search"),
    url(r'^committees/add/$', 'add', name='committees.add'),
    url(r'^committees/edit/(?P<id>\d+)/$', 'edit', name='committees.edit'),
    url(r'^committees/edit/meta/(?P<id>\d+)/$', 'edit_meta', name="committees.edit.meta"),
    url(r'^committees/delete/(?P<id>\d+)/$', 'delete', name='committees.delete'),
    url(r'^committees/feed/$', LatestEntriesFeed(), name='committees.feed'),
    url(r'^committees/(?P<slug>[\w\-\/]+)/$', 'detail', name="committees.detail"),
)
