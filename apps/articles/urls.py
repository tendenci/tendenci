from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',                  
    url(r'^$', 'articles.views.articles', name="articles"),
#    url(r'^add/$', 'articles.views.add', name="article_add"),
#    url(r'^edit/(\d+)/$', 'articles.views.edit', name="article_edit"),
#    url(r'^delete/(\d+)/$', 'articles.views.delete', name="article_delete"),     
#    url(r'^([\d\w\-\/]+)/$', 'articles.views.details', name="article_details"),
)