from django.conf.urls import patterns, url

urlpatterns = patterns('tendenci.apps.exports.views',
    url(r'^(?P<export_id>\d+)/$', 'status', name="export.status"),
    url(r'^(?P<export_id>\d+)/download/$', 'download', name="export.download"),
)

