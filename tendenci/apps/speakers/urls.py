from django.conf.urls import patterns, url
from tendenci.apps.speakers.feeds import LatestEntriesFeed

urlpatterns = patterns('tendenci.apps.speakers.views',
    url(r'^speakers/$', 'search', name="speakers"),
    url(r'^speakers/search/$', 'search_redirect', name="speaker.search"),
    url(r'^speakers/feed/$', LatestEntriesFeed(), name='speaker.feed'),
    url(r'^speakers/(?P<slug>[\w\-]+)/$', 'details', name="speaker.view"),
)