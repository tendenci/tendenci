from django.conf.urls.defaults import patterns, url
from tendenci.apps.pages.feeds import LatestEntriesFeed
from tendenci.core.site_settings.utils import get_setting

urlpath = get_setting('module', 'pages', 'url')
if not urlpath:
    urlpath = "pages"

urlpatterns = patterns('tendenci.apps.pages.views',
    url(r'^%s/$' % urlpath, 'index', name="pages"),
    url(r'^%s/search/$' % urlpath, 'search', name="page.search"),
    url(r'^%s/print-view/(?P<slug>[\w\-\/]+)/$' % urlpath, 'print_view', name="page.print_view"),
    url(r'^%s/export/$' % urlpath, 'export', name="page.export"),
    url(r'^%s/preview/$' % urlpath, 'preview', name="page.preview"),
    url(r'^%s/preview/(?P<id>\d+)/$' % urlpath, 'preview', name="page.preview"),
    url(r'^%s/add/$' % urlpath, 'add', name="page.add"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, 'edit', name="page.edit"),
    url(r'^%s/versions/(?P<hash>[\w\-]+)/$' % urlpath, 'index', name="page.version"),
    url(r'^%s/inactive/(?P<id>\d+)/$' % urlpath, 'index', name="page.inactive"),
    url(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, 'edit_meta', name="page.edit.meta"),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, 'delete', name="page.delete"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='page.feed'),
    url(r'^%s/header_image/(?P<id>\d+)/$' % urlpath, 'display_header_image', name="page.header_image"),
)
