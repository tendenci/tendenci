from django.conf.urls.defaults import patterns, url
from tendenci.apps.stories.feeds import LatestEntriesFeed

urlpatterns = patterns('tendenci.apps.stories.views',
    url(r'^$', 'search', name="stories"),
    url(r'^(?P<id>\d+)/$', 'details', name="story"),
    url(r'^print/(?P<id>\d+)/$', 'print_details', name="story.print_details"),
    url(r'^search/$', 'search_redirect', name="story.search"),
    url(r'^add/$', 'add', name="story.add"),
    url(r'^edit/(?P<id>\d+)/$', 'edit', name="story.edit"),
    url(r'^delete/(?P<id>\d+)/$', 'delete', name="story.delete"),
    url(r'^export/$', 'export', name="story.export"),
    url(r'^feed/$', LatestEntriesFeed(), name='story.feed'),
)
