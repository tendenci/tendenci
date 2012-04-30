from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('exports',
    url(r'^(?P<task_id>[-\w]+)/$', 'views.status', name="export.status"),
    url(r'^(?P<task_id>[-\w]+)/download/$', 'views.download', name="export.download"),
)

