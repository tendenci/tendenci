from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('tendenci.apps.explorer_extensions.views',
    url(r'^export_database/$', 'export_page', name="explorer_extensions.export_page"),
    url(r'^export/(?P<dump_id>\d+)/download/$', 'download_dump', name="explorer_extensions.download_dump"),
    url(r'^export/(?P<dump_id>\d+)/delete/$', 'delete_dump', name="explorer_extensions.delete_dump"),
)
