from django.conf.urls.defaults import patterns, url
from tendenci.addons.articles.feeds import LatestEntriesFeed
from tendenci.core.site_settings.utils import get_setting
from tendenci.addons.articles.signals import init_signals

init_signals()

urlpath = get_setting('module', 'articles', 'url') or 'articles'
urlpatterns = patterns('tendenci.addons.articles.views',
    url(r'^%s/$'        % urlpath, 'search', name="articles"),
    url(r'^%s/search/$' % urlpath, 'search_redirect', name="article.search"),
    url(r'^%s/print-view/(?P<slug>[\w\-\/]+)/$'
                        % urlpath, 'print_view', name="article.print_view"),
    url(r'^%s/add/$'    % urlpath, 'add', name="article.add"),
    url(r'^%s/edit/(?P<id>\d+)/$'
                        % urlpath, 'edit', name="article.edit"),
    url(r'^%s/edit/meta/(?P<id>\d+)/$'
                        % urlpath, 'edit_meta', name="article.edit.meta"),
    url(r'^%s/delete/(?P<id>\d+)/$'
                        % urlpath, 'delete', name="article.delete"),
    url(r'^%s/feed/$'   % urlpath, LatestEntriesFeed(), name='article.feed'),
    url(r'^%s/export/$' % urlpath, 'export', name='article.export'),
    url(r'^%s/export/status/(?P<identifier>\d+)/$' % urlpath, 'export_status', name='article.export_status'),
    url(r'^%s/export/download/(?P<identifier>\d+)/$' % urlpath, 'export_download', name='article.export_download'),
    url(r'^%s/reports/rank/$'
                        % urlpath, 'articles_report', name='reports-articles'),
    url(r'^%s/versions/(?P<hash>[\w\-]+)/$'
                        % urlpath, 'detail', name="article.version"),
    url(r'^%s/(?P<slug>[\w\-\/]+)/$'
                        % urlpath, 'detail', name="article"),
)
