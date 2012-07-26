from django.conf.urls.defaults import patterns, url
from tendenci.apps.products.feeds import LatestEntriesFeed

urlpatterns = patterns('tendenci.apps.products.views',
    url(r'^products/$', 'search', name="products"),
    url(r'^products/search/$', 'search_redirect', name="products.search"),
    url(r'^products/feed/$', LatestEntriesFeed(), name='products.feed'),
    url(r'^products/(?P<slug>[\w\-\/]+)/$', 'detail', name="products.detail"),
)