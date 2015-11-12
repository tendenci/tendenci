from django.conf.urls import url
from tendenci.apps.pages.feeds import LatestEntriesFeed
from tendenci.apps.site_settings.utils import get_setting
from . import views

urlpath = get_setting('module', 'pages', 'url')
if not urlpath:
    urlpath = "pages"

urlpatterns = [
    url(r'^%s/$' % urlpath, views.index, name="pages"),
    url(r'^%s/search/$' % urlpath, views.search, name="page.search"),
    url(r'^%s/print-view/(?P<slug>[\w\-\/]+)/$' % urlpath, views.print_view, name="page.print_view"),
    url(r'^%s/export/$' % urlpath, views.export, name="page.export"),
    url(r'^%s/preview/$' % urlpath, views.preview, name="page.preview"),
    url(r'^%s/preview/(?P<id>\d+)/$' % urlpath, views.preview, name="page.preview"),
    url(r'^%s/add/$' % urlpath, views.add, name="page.add"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="page.edit"),
    url(r'^%s/versions/(?P<hash>[\w\-]+)/$' % urlpath, views.index, name="page.version"),
    url(r'^%s/inactive/(?P<id>\d+)/$' % urlpath, views.index, name="page.inactive"),
    url(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, views.edit_meta, name="page.edit.meta"),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="page.delete"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='page.feed'),
    url(r'^%s/header_image/(?P<id>\d+)/$' % urlpath, views.display_header_image, name="page.header_image"),
]
