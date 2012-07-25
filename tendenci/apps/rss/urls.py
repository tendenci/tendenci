from django.conf.urls.defaults import patterns, url
from tendenci.apps.rss.feeds import GlobalFeed

urlpatterns = patterns('',
    url(r'^$', GlobalFeed(), name="rss.mainrssfeed"),
)
