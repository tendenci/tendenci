from django.conf.urls import patterns, url

urlpatterns = patterns('tendenci.apps.wp_exporter.views',
    url(r'^$', 'index', name="wp_exporter"),
    url(r'^detail/(?P<task_id>[-\w]+)/$', 'detail', name='export_detail'),
    url(r'^download/(?P<export_id>\d+)/$', 'download'),
)
