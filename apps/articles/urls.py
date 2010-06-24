from django.conf.urls.defaults import patterns, url
from articles.feeds import LatestEntriesFeed

urlpatterns = patterns('articles',                  
    url(r'^$', 'views.index', name="articles"),
    url(r'^(?P<id>\d+)/$', 'views.index', name="article"),
    url(r'^search/$', 'views.search', name="article.search"),
    url(r'^print-view/(?P<id>\d+)/$', 'views.print_view', name="article.print_view"),
    url(r'^add/$', 'views.add', name="article.add"),
    url(r'^edit/(?P<id>\d+)/$', 'views.edit', name="article.edit"),
    url(r'^edit/meta/(?P<id>\d+)/$', 'views.edit_meta', name="article.edit.meta"),
    url(r'^delete/(?P<id>\d+)/$', 'views.delete', name="article.delete"),
    url(r'^feed/$', LatestEntriesFeed(), name='article.feed'),
)