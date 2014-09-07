from django.conf.urls import patterns, include, url

urlpatterns = patterns('tendenci.apps.wp_importer.views',
    url(r'^$', 'index'),
    url(r'^detail/(?P<task_id>[-\w]+)/$', 'detail', name='detail'),
)
