from django.conf.urls.defaults import patterns, url
from tendenci.addons.news.feeds import LatestEntriesFeed

urlpatterns = patterns('tendenci.addons.news.views',
    url(r'^$', 'search', name="news"),
    url(r'^search/$', 'search_redirect', name="news.search"),
    url(r'^print-view/(?P<slug>[\w\-\/]+)/$', 'print_view', name="news.print_view"),
    url(r'^add/$', 'add', name="news.add"),
    url(r'^edit/(?P<id>\d+)/$', 'edit', name="news.edit"),
    url(r'^edit/meta/(?P<id>\d+)/$', 'edit_meta', name="news.edit.meta"),
    url(r'^delete/(?P<id>\d+)/$', 'delete', name="news.delete"),
    url(r'^feed/$', LatestEntriesFeed(), name='news.feed'),
    url(r'^export/$', 'export', name='news.export'),
    url(r'^(?P<slug>[\w\-\/]+)/$', 'detail', name="news.detail"),
)
