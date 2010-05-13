from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',                  
    url(r'^$', 'articles.views.index', name="articles"),
    url(r'^(?P<id>\d+)/$', 'articles.views.index', name="article"),
    url(r'^search/$', 'articles.views.search', name="article.search"),
    url(r'^print-view/(?P<id>\d+)/$', 'articles.views.print_view', name="article.print_view"),
    url(r'^edit/(?P<id>\d+)/$', 'articles.views.edit', name="article.edit"),
    url(r'^delete/(?P<id>\d+)/$', 'articles.views.delete', name="article.delete"),
)