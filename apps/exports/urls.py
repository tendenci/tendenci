from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('exports',
    url(r'^(?P<export_id>\d+)/$', 'views.status', name="export.status"),
    url(r'^(?P<export_id>\d+)/download/$', 'views.download', name="export.download"),
)

