from django.conf.urls.defaults import patterns, url
from stories.feeds import LatestEntriesFeed

urlpatterns = patterns('',                  
    url(r'^$', 'stories.views.index', name="stories"),
    url(r'^(?P<id>\d+)/$', 'stories.views.index', name="story"),
    url(r'^print/(?P<id>\d+)/$', 'stories.views.print_details', name="story.print_details"),
    url(r'^search/$', 'stories.views.search', name="story.search"),
    url(r'^add/$', 'stories.views.add', name="story.add"),
    url(r'^edit/(?P<id>\d+)/$', 'stories.views.edit', name="story.edit"),
    url(r'^upload/(?P<id>\d+)/$', 'stories.views.upload', name="story.upload"),
    url(r'^delete/(?P<id>\d+)/$', 'stories.views.delete', name="story.delete"),
    url(r'^feed/$', LatestEntriesFeed(), name='story.feed'),
)