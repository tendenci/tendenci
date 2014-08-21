from django.conf.urls.defaults import patterns, url
from tendenci.addons.locations.feeds import LatestEntriesFeed
from tendenci.core.site_settings.utils import get_setting
from tendenci.addons.locations.signals import init_signals

init_signals()

urlpath = get_setting('module', 'locations', 'url')
if not urlpath:
    urlpath = "locations"

urlpatterns = patterns('tendenci.addons.locations.views',
    url(r'^%s/$' % urlpath, 'search', name="locations"),
    url(r'^%s/search/$' % urlpath, 'search_redirect', name="location.search"),
    url(r'^%s/nearest/$' % urlpath, 'nearest', name="location.nearest"),
    url(r'^%s/print-view/(?P<id>\d+)/$' % urlpath, 'print_view', name="location.print_view"),
    url(r'^%s/add/$' % urlpath, 'add', name="location.add"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, 'edit', name="location.edit"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='locations.feed'),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, 'delete', name="location.delete"),
    url(r'^%s/(?P<id>[-\w]+)/$' % urlpath, 'detail', name="location"),
    url(r'^locations/import/$', 'locations_import_upload', name='locations_import_upload_file'),
    url(r'^locations/import/preview/(?P<id>\d+)/$', 'locations_import_preview', name='locations_import_preview'),
    url(r'^locations/import/confirm/(?P<id>\d+)/$', 'locations_import_confirm', name='locations_import_confirm'),
    url(r'^locations/import/status/(?P<task_id>[-\w]+)/$', 'locations_import_status', name='locations_import_status'),
    url(r'^locations/upload/formats/csv/$', 'download_location_upload_template',
            name="locations.download_location_upload_template_csv"),
    url(r'^%s/export/$' % urlpath, 'export', name='locations_export'),

)
