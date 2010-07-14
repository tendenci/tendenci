from django.conf.urls.defaults import patterns, url
from rss.feeds import MainRSSFeed

urlpatterns = patterns('',                  
    url(r'^$', MainRSSFeed(), name="rss.mainrssfeed"),
    #url(r'^podcasts/$', MainPodcasts, name="rss.mainpodcasts"),
)