from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',                  
    url(r'^$', 'articles.views.index', name="articles"),
    url(r'^search/$', 'articles.views.search', name="article.search"),
    url(r'^view/$', 'articles.views.view', name="article.view"),
    url(r'^print-view/$', 'articles.views.print_view', name="article.print_view"),
    url(r'^edit/$', 'articles.views.edit', name="article.edit"),
    url(r'^delete/$', 'articles.views.delete', name="article.delete"),
)