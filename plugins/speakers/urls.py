from django.conf.urls.defaults import patterns, url
from feeds import LatestEntriesFeed

urlpatterns = patterns('speakers.views',
    url(r'^speakers/$', 'index', name="speaker"),
    url(r'^speakers/search/$', 'search', name="speaker.search"),
    url(r'^speakers/feed/$', LatestEntriesFeed(), name='speaker.feed'),
    url(r'^speakers/(?P<slug>[\w\-]+)/$', 'index', name="speaker.view"),
)