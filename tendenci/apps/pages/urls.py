from django.conf.urls.defaults import patterns, url
from tendenci.apps.pages.feeds import LatestEntriesFeed

urlpatterns = patterns('tendenci.apps.pages.views',
    url(r'^$', 'index', name="pages"),
    url(r'^search/$', 'search', name="page.search"),
    url(r'^print-view/(?P<slug>[\w\-\/]+)/$', 'print_view', name="page.print_view"),
    url(r'^export/$', 'export', name="page.export"),
    url(r'^add/$', 'add', name="page.add"),
    url(r'^edit/(?P<id>\d+)/$', 'edit', name="page.edit"),
    url(r'^versions/(?P<hash>[\w\-]+)/$', 'index', name="page.version"),
    url(r'^inactive/(?P<id>\d+)/$', 'index', name="page.inactive"),
    url(r'^edit/meta/(?P<id>\d+)/$', 'edit_meta', name="page.edit.meta"),
    url(r'^delete/(?P<id>\d+)/$', 'delete', name="page.delete"),
    url(r'^feed/$', LatestEntriesFeed(), name='page.feed'),
)
