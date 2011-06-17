from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('attorneys.views',
    url(r'^attorneys/$', 'search', name="attorneys.search"),
    url(r'^attorneys/(?P<id>\d+)/$', 'detail', name="attorneys.detail"),
)
