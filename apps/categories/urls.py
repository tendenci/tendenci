from django.conf.urls.defaults import patterns, url
from articles.feeds import LatestEntriesFeed

urlpatterns = patterns('categories',                  
    url(r'^update/(?P<app_label>\w+)/(?P<model>\w+)/(?P<pk>[\w\d]+)/$', 
        'views.add', name="category.update"),
)