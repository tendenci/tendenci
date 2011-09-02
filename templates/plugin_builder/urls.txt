from django.conf.urls.defaults import patterns, url
from S_P_LOW.feeds import LatestEntriesFeed

urlpatterns = patterns('S_P_LOW.views',                  
    url(r'^S_P_LOW/$', 'index', name="S_P_LOW"),
    url(r'^S_P_LOW/search/$', 'search', name="S_P_LOW.search"),
    url(r'^S_P_LOW/feed/$', LatestEntriesFeed(), name='S_P_LOW.feed'),
    url(r'^S_P_LOW/(?P<pk>[\d/]+)/$', 'detail', name="S_P_LOW.detail"),
)