from django.conf.urls.defaults import patterns, url
from locations.feeds import LatestEntriesFeed
from site_settings.utils import get_setting

urlpath = get_setting('module', 'locations', 'url')
if not urlpath:
    urlpath = "locations"

urlpatterns = patterns('',                  
    url(r'^%s/$' % urlpath, 'locations.views.search', name="locations"),
    url(r'^%s/(?P<id>\d+)/$' % urlpath, 'locations.views.index', name="location"),
    url(r'^%s/search/$' % urlpath, 'locations.views.search_redirect', name="location.search"),
    url(r'^%s/nearest/$' % urlpath, 'locations.views.nearest', name="location.nearest"),
    url(r'^%s/print-view/(?P<id>\d+)/$' % urlpath, 'locations.views.print_view', name="location.print_view"),
    url(r'^%s/add/$' % urlpath, 'locations.views.add', name="location.add"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, 'locations.views.edit', name="location.edit"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='locations.feed'),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, 'locations.views.delete', name="location.delete"),
)