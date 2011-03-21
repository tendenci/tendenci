from django.conf.urls.defaults import patterns, url
from feeds import LatestEntriesFeed

urlpatterns = patterns('staff.views',
    url(r'^staff/$', 'index', name="staff"),
    url(r'^staff/search/$', 'search', name="staff.search"),
    url(r'^staff/feed/$', LatestEntriesFeed(), name='staff.feed'),
    url(r'^staff/(?P<slug>[\w\-]+)/$', 'index', name="staff.view"),
    url(r'^staff/(?P<slug>[\w\-]+)/(?P<cv>cv)/$', 'index', name="staff.cv"),
)