from django.conf.urls import patterns, url
from tendenci.apps.news.feeds import LatestEntriesFeed
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.news.signals import init_signals

init_signals()

urlpath = get_setting('module', 'news', 'url')
if not urlpath:
    urlpath = "news"

urlpatterns = patterns('tendenci.apps.news.views',
    url(r'^%s/$' % urlpath, 'search', name="news"),
    url(r'^%s/search/$' % urlpath, 'search_redirect', name="news.search"),
    url(r'^%s/print-view/(?P<slug>[\w\-\/]+)/$' % urlpath, 'print_view', name="news.print_view"),
    url(r'^%s/add/$' % urlpath, 'add', name="news.add"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, 'edit', name="news.edit"),
    url(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, 'edit_meta', name="news.edit.meta"),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, 'delete', name="news.delete"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='news.feed'),
    url(r'^%s/export/$' % urlpath, 'export', name='news.export'),
    url(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, 'detail', name="news.detail"),
)
