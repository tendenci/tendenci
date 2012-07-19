from django.conf.urls.defaults import patterns, url
from rss.feeds import GlobalFeed, MainRSSFeed

urlpatterns = patterns('',                  
    url(r'^$', GlobalFeed(), name="rss.mainrssfeed"),
    #url(r'^podcasts/$', MainPodcasts, name="rss.mainpodcasts"),
)
