from django.conf.urls.defaults import patterns, url
from tendenci.apps.quotes.feeds import LatestEntriesFeed

urlpatterns = patterns('tendenci.apps.quotes.views',
    url(r'^quotes/$', 'search', name="quotes"),
    url(r'^quotes/search/$', 'search_redirect', name="quote.search"),
    url(r'^quotes/feed/$', LatestEntriesFeed(), name='quote.feed'),
    url(r'^quotes/(?P<pk>[\d/]+)/$', 'detail', name="quote.view"),
)