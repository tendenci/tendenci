from django.conf.urls.defaults import patterns, url
from products.feeds import LatestEntriesFeed

urlpatterns = patterns('products.views',                  
    url(r'^products/$', 'search', name="products"),
    url(r'^products/search/$', 'search_redirect', name="products.search"),
    url(r'^products/feed/$', LatestEntriesFeed(), name='products.feed'),
    url(r'^products/(?P<slug>[\w\-\/]+)/$', 'details', name="products.detail"),
)