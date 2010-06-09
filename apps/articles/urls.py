from django.conf.urls.defaults import patterns, url
from articles.feeds import LatestEntriesFeed

urlpatterns = patterns('',                  
    url(r'^$', 'articles.views.index', name="articles"),
    url(r'^(?P<id>\d+)/$', 'articles.views.index', name="article"),
    url(r'^search/$', 'articles.views.search', name="article.search"),
    url(r'^print-view/(?P<id>\d+)/$', 'articles.views.print_view', name="article.print_view"),
    url(r'^add/$', 'articles.views.add', name="article.add"),
    url(r'^edit/(?P<id>\d+)/$', 'articles.views.edit', name="article.edit"),
    url(r'^delete/(?P<id>\d+)/$', 'articles.views.delete', name="article.delete"),
    url(r'^feed/$', LatestEntriesFeed(), name='article.feed'),
)