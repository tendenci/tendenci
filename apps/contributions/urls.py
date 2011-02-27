from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('contributions',                  
    url(r'^$', 'views.index', name="contribution"),
    url(r'^(?P<id>\d+)/$', 'views.index', name="contribution"),
    url(r'^search/$', 'views.search', name="contribution.search"),
)