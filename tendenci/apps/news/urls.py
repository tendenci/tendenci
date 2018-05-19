from django.conf.urls import url
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed


urlpath = get_setting('module', 'news', 'url')
if not urlpath:
    urlpath = "news"

urlpatterns = [
    url(r'^%s/$' % urlpath, views.search, name="news"),
    url(r'^%s/(?P<release_year>\d{4})/$' % urlpath, views.search, name="news_by_release_year"),
    url(r'^%s/search/$' % urlpath, views.search_redirect, name="news.search"),
    url(r'^%s/print-view/(?P<slug>[\w\-\/]+)/$' % urlpath, views.print_view, name="news.print_view"),
    url(r'^%s/add/$' % urlpath, views.add, name="news.add"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="news.edit"),
    url(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, views.edit_meta, name="news.edit.meta"),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="news.delete"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='news.feed'),
    url(r'^%s/export/$' % urlpath, views.export, name='news.export'),
    url(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, views.detail, name="news.detail"),
]
