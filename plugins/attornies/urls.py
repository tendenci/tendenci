from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('attornies.views',
    url(r'^attornies/$', 'search', name="attornies.search"),
    url(r'^attornies/(?P<id>\d+)/$', 'detail', name="attornies.detail"),
)
