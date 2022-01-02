from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.locations.signals import init_signals
from . import views
from .feeds import LatestEntriesFeed

init_signals()

urlpath = get_setting('module', 'locations', 'url')
if not urlpath:
    urlpath = "locations"

urlpatterns = [
    re_path(r'^%s/$' % urlpath, views.search, name="locations"),
    re_path(r'^%s/search/$' % urlpath, views.search_redirect, name="location.search"),
    re_path(r'^%s/nearest/$' % urlpath, views.nearest, name="location.nearest"),
    re_path(r'^%s/print-view/(?P<id>\d+)/$' % urlpath, views.print_view, name="location.print_view"),
    re_path(r'^%s/add/$' % urlpath, views.add, name="location.add"),
    re_path(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="location.edit"),
    re_path(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='locations.feed'),
    re_path(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="location.delete"),
    re_path(r'^locations/import/$', views.locations_import_upload, name='locations_import_upload_file'),
    re_path(r'^locations/import/preview/(?P<id>\d+)/$', views.locations_import_preview, name='locations_import_preview'),
    re_path(r'^locations/import/confirm/(?P<id>\d+)/$', views.locations_import_confirm, name='locations_import_confirm'),
    re_path(r'^locations/import/status/(?P<task_id>[-\w]+)/$', views.locations_import_status, name='locations_import_status'),
    re_path(r'^locations/upload/formats/csv/$', views.download_location_upload_template,
            name="locations.download_location_upload_template_csv"),
    re_path(r'^%s/export/$' % urlpath, views.export, name='locations_export'),
    re_path(r'^%s/(?P<slug>[-\w]+)/$' % urlpath, views.detail, name="location"),

]
