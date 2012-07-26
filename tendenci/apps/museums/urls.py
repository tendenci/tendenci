from django.conf.urls.defaults import patterns, url
from tendenci.apps.museums.feeds import LatestEntriesFeed

urlpatterns = patterns('tendenci.apps.museums.views',
    url(r'^museums/$', 'search', name="museums"),
    url(r'^museums/search/$', 'search_redirect', name="museums.search"),
    url(r'^museums/feed/$', LatestEntriesFeed(), name='museums.feed'),
    url(r'^museums/(?P<slug>[\w\-]+)/$', 'detail', name="museums.detail"),
)