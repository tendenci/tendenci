from django.conf.urls.defaults import patterns, url
from quotes.feeds import LatestEntriesFeed

urlpatterns = patterns('quotes.views',                  
    url(r'^quotes/$', 'search', name="quotes"),
    url(r'^quotes/search/$', 'search_redirect', name="quote.search"),
    url(r'^quotes/feed/$', LatestEntriesFeed(), name='quote.feed'),
    url(r'^quotes/(?P<pk>[\d/]+)/$', 'details', name="quote.view"),
)