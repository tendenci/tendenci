from django.conf.urls.defaults import patterns, url
from articles.feeds import LatestEntriesFeed

urlpatterns = patterns('dashboard',                  
    url(r'^$', 'views.index', name="dashboard"),
)