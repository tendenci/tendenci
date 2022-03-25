from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed

urlpath = get_setting('module', 'articles', 'url') or 'articles'

urlpatterns = [
    re_path(r'^%s/$' % urlpath, views.search, name="articles"),
    path('%s/search/' % urlpath, views.search_redirect, name="article.search"),
    re_path(r'^%s/print-view/(?P<slug>[\w\-\/]+)/$' % urlpath, views.print_view, name="article.print_view"),
    path('%s/add/' % urlpath, views.add, name="article.add"),
    re_path(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="article.edit"),
    re_path(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, views.edit_meta, name="article.edit.meta"),
    re_path(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="article.delete"),
    path('%s/feed/' % urlpath, LatestEntriesFeed(), name='article.feed'),
    path('%s/export/' % urlpath, views.export, name='article.export'),
    re_path(r'^%s/export/status/(?P<identifier>\d+)/$' % urlpath, views.export_status, name='article.export_status'),
    re_path(r'^%s/export/download/(?P<identifier>\d+)/$' % urlpath, views.export_download, name='article.export_download'),
    path('%s/reports/rank/' % urlpath, views.articles_report, name='reports-articles'),
    re_path(r'^%s/versions/(?P<hash>[\w\-]+)/$' % urlpath, views.detail, name="article.version"),
    re_path(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, views.detail, name="article"),
]
