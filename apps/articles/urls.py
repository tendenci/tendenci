from django.conf.urls.defaults import patterns, url
from articles.feeds import LatestEntriesFeed
from site_settings.utils import get_setting

urlpath = get_setting('module', 'articles', 'url')
print urlpath
if not urlpath:
    urlpath = "articles"

urlpatterns = patterns('articles',
    url(r'^%s/$' % urlpath, 'views.list', name="articles"),
    url(r'^%s/search/$' % urlpath, 'views.search', name="article.search"),
    url(r'^%s/print-view/(?P<slug>[\w\-\/]+)/$' % urlpath, 'views.print_view', name="article.print_view"),
    url(r'^%s/add/$' % urlpath, 'views.add', name="article.add"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, 'views.edit', name="article.edit"),
    url(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, 'views.edit_meta', name="article.edit.meta"),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, 'views.delete', name="article.delete"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='article.feed'),
    url(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, 'views.index', name="article"),
)