from django.conf.urls.defaults import patterns, url
from museums.feeds import LatestEntriesFeed

urlpatterns = patterns('museums.views',                  
    url(r'^museums/$', 'index', name="museums"),
    url(r'^museums/search/$', 'search', name="museums.search"),
    url(r'^museums/feed/$', LatestEntriesFeed(), name='museums.feed'),
    url(r'^museums/(?P<slug>[\w\-]+)/$', 'detail', name="museums.detail"),
)