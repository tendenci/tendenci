from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('tendenci.apps.explorer_extensions.views',
    url(r'^export_database/$', 'export_page', name="explorer_extensions.export_page"),
)
