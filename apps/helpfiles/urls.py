from django.conf.urls.defaults import *

urlpatterns = patterns('helpfiles.views',
    url(r'^$', 'home', name='helpfiles'),
    url(r'^topic/(?P<id>\d+)/$', 'topic', name='helpfiles-topic'),
    url(r'^(?P<id>\d+)/$', 'details', name='helpfiles-details'),
    url(r'^request/$', 'request_new', name='helpfiles-new'),
)
