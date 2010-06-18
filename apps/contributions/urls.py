from django.conf.urls.defaults import patterns, url
from contributions.feeds import LatestEntriesFeed

urlpatterns = patterns('contributions',                  
    url(r'^$', 'views.index', name="contribution"),
    url(r'^(?P<id>\d+)/$', 'views.index', name="contribution"),
    url(r'^search/$', 'views.search', name="contribution.search"),
    url(r'^print-view/(?P<id>\d+)/$', 'views.print_view', name="contribution.print_view"),
    url(r'^feed/$', LatestEntriesFeed(), name='contribution.feed'),
)