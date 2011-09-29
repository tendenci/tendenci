from django.conf.urls.defaults import *

urlpatterns = patterns('help_files.views',
    url(r'^$', 'index', name='help_files'),
    url(r'^search/$', 'search', name='help_files.search'),
    url(r'^topic/(?P<id>\d+)/$', 'topic', name='help_files.topic'),
    url(r'^requests/$', 'requests', name='help_files.requests'),
    url(r'^request/$', 'request_new', name='help_files.request'),
    url(r'^(?P<slug>[\w\-\/]+)/$', 'details', name='help_file.details'),
)
