from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('base',
    url(r'^image-preview/(?P<app_label>\w+)/(?P<model>\w+)/(?P<id>\d+)/(?P<size>(\d+|\d+x\d+))/$', 'views.image_preview', name="image_preview"),
    url(r'^feedback/$', 'views.feedback', name='tendenci_feedback'),
    url(r'^memcached-status/$', 'views.memcached_status', name='memcached_status'),
    url(r'^clear-cache/$', 'views.clear_cache', name='clear_cache'),
)
