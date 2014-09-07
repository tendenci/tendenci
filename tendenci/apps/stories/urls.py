from django.conf.urls import patterns, url
from tendenci.apps.stories.feeds import LatestEntriesFeed
from tendenci.apps.site_settings.utils import get_setting

urlpath = get_setting('module', 'stories', 'url')
if not urlpath:
    urlpath = "stories"

urlpatterns = patterns('tendenci.apps.stories.views',
    url(r'^%s/$' % urlpath, 'search', name="stories"),
    url(r'^%s/(?P<id>\d+)/$' % urlpath, 'details', name="story"),
    url(r'^%s/print/(?P<id>\d+)/$' % urlpath, 'print_details', name="story.print_details"),
    url(r'^%s/search/$' % urlpath, 'search_redirect', name="story.search"),
    url(r'^%s/add/$' % urlpath, 'add', name="story.add"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, 'edit', name="story.edit"),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, 'delete', name="story.delete"),
    url(r'^%s/export/$' % urlpath, 'export', name="story.export"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='story.feed'),
)
