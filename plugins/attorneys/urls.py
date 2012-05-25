from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('attorneys.views',
    url(r'^attorneys/$', 'index', name="attorneys"),
    url(r'^attorneys/search/$', 'search', name="attorneys.search"),
    url(r'^attorneys/(?P<slug>[\w\-]+)/vcard/$', 'vcard', name="attorneys.vcard"),
    url(r'^attorneys/(?P<slug>[\w\-]+)/$', 'detail', name="attorneys.detail"),
)
