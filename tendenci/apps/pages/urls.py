from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed

urlpath = get_setting('module', 'pages', 'url')
if not urlpath:
    urlpath = "pages"

urlpatterns = [
    re_path(r'^%s/$' % urlpath, views.index, name="pages"),
    re_path(r'^%s/search/$' % urlpath, views.search, name="page.search"),
    re_path(r'^%s/print-view/(?P<slug>[\w\-\/]+)/$' % urlpath, views.print_view, name="page.print_view"),
    re_path(r'^%s/export/$' % urlpath, views.export, name="page.export"),
    re_path(r'^%s/preview/$' % urlpath, views.preview, name="page.preview"),
    re_path(r'^%s/preview/(?P<id>\d+)/$' % urlpath, views.preview, name="page.preview"),
    re_path(r'^%s/add/$' % urlpath, views.add, name="page.add"),
    re_path(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="page.edit"),
    re_path(r'^%s/versions/(?P<hash>[\w\-]+)/$' % urlpath, views.index, name="page.version"),
    re_path(r'^%s/inactive/(?P<id>\d+)/$' % urlpath, views.index, name="page.inactive"),
    re_path(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, views.edit_meta, name="page.edit.meta"),
    re_path(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="page.delete"),
    re_path(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='page.feed'),
    re_path(r'^%s/header_image/(?P<id>\d+)/$' % urlpath, views.display_header_image, name="page.header_image"),
]
