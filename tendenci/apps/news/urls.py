from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed


urlpath = get_setting('module', 'news', 'url')
if not urlpath:
    urlpath = "news"

urlpatterns = [
    re_path(r'^%s/$' % urlpath, views.search, name="news"),
    re_path(r'^%s/(?P<release_year>\d{4})/$' % urlpath, views.search, name="news_by_release_year"),
    re_path(r'^%s/search/$' % urlpath, views.search_redirect, name="news.search"),
    re_path(r'^%s/print-view/(?P<slug>[\w\-\/]+)/$' % urlpath, views.print_view, name="news.print_view"),
    re_path(r'^%s/add/$' % urlpath, views.add, name="news.add"),
    re_path(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="news.edit"),
    re_path(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, views.edit_meta, name="news.edit.meta"),
    re_path(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="news.delete"),
    re_path(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='news.feed'),
    re_path(r'^%s/export/$' % urlpath, views.export, name='news.export'),
    re_path(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, views.detail, name="news.detail"),
]
