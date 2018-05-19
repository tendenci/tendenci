from django.conf.urls import url
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed

urlpath = get_setting('module', 'articles', 'url') or 'articles'

urlpatterns = [
    url(r'^%s/$' % urlpath, views.search, name="articles"),
    url(r'^%s/search/$' % urlpath, views.search_redirect, name="article.search"),
    url(r'^%s/print-view/(?P<slug>[\w\-\/]+)/$' % urlpath, views.print_view, name="article.print_view"),
    url(r'^%s/add/$' % urlpath, views.add, name="article.add"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="article.edit"),
    url(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, views.edit_meta, name="article.edit.meta"),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="article.delete"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='article.feed'),
    url(r'^%s/export/$' % urlpath, views.export, name='article.export'),
    url(r'^%s/export/status/(?P<identifier>\d+)/$' % urlpath, views.export_status, name='article.export_status'),
    url(r'^%s/export/download/(?P<identifier>\d+)/$' % urlpath, views.export_download, name='article.export_download'),
    url(r'^%s/reports/rank/$' % urlpath, views.articles_report, name='reports-articles'),
    url(r'^%s/versions/(?P<hash>[\w\-]+)/$' % urlpath, views.detail, name="article.version"),
    url(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, views.detail, name="article"),
]
