from django.conf.urls.defaults import patterns, url
from tendenci.apps.locations.feeds import LatestEntriesFeed
from tendenci.core.site_settings.utils import get_setting

urlpath = get_setting('module', 'locations', 'url')
if not urlpath:
    urlpath = "locations"

urlpatterns = patterns('tendenci.apps.locations.views',
    url(r'^%s/$' % urlpath, 'search', name="locations"),
    url(r'^%s/(?P<id>\d+)/$' % urlpath, 'detail', name="location"),
    url(r'^%s/search/$' % urlpath, 'search_redirect', name="location.search"),
    url(r'^%s/nearest/$' % urlpath, 'nearest', name="location.nearest"),
    url(r'^%s/print-view/(?P<id>\d+)/$' % urlpath, 'print_view', name="location.print_view"),
    url(r'^%s/add/$' % urlpath, 'add', name="location.add"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, 'edit', name="location.edit"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='locations.feed'),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, 'delete', name="location.delete"),
    # import
    url(r'^%s/import/$' % urlpath, 'locations_import_upload', name='locations_import_upload_file'),
    url(r'^%s/import/preview/(?P<id>\d+)/$' % urlpath, 'locations_import_preview', name='locations_import_preview'),
    url(r'^%s/import/confirm/(?P<id>\d+)/$' % urlpath, 'locations_import_confirm', name='locations_import_confirm'),
    url(r'^%s/import/status/(?P<task_id>[-\w]+)/$' % urlpath, 'locations_import_status', name='locations_import_status'),
    # export
    url(r'^%s/export/$' % urlpath, 'export', name='locations_export'),
)
