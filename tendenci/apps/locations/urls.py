from django.conf.urls import url
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.locations.signals import init_signals
from . import views
from .feeds import LatestEntriesFeed

init_signals()

urlpath = get_setting('module', 'locations', 'url')
if not urlpath:
    urlpath = "locations"

urlpatterns = [
    url(r'^%s/$' % urlpath, views.search, name="locations"),
    url(r'^%s/search/$' % urlpath, views.search_redirect, name="location.search"),
    url(r'^%s/nearest/$' % urlpath, views.nearest, name="location.nearest"),
    url(r'^%s/print-view/(?P<id>\d+)/$' % urlpath, views.print_view, name="location.print_view"),
    url(r'^%s/add/$' % urlpath, views.add, name="location.add"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="location.edit"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='locations.feed'),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="location.delete"),
    url(r'^locations/import/$', views.locations_import_upload, name='locations_import_upload_file'),
    url(r'^locations/import/preview/(?P<id>\d+)/$', views.locations_import_preview, name='locations_import_preview'),
    url(r'^locations/import/confirm/(?P<id>\d+)/$', views.locations_import_confirm, name='locations_import_confirm'),
    url(r'^locations/import/status/(?P<task_id>[-\w]+)/$', views.locations_import_status, name='locations_import_status'),
    url(r'^locations/upload/formats/csv/$', views.download_location_upload_template,
            name="locations.download_location_upload_template_csv"),
    url(r'^%s/export/$' % urlpath, views.export, name='locations_export'),
    url(r'^%s/(?P<slug>[-\w]+)/$' % urlpath, views.detail, name="location"),

]
