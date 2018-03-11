from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^export_database/$', views.export_page, name="explorer_extensions.export_page"),
    url(r'^export/(?P<dump_id>\d+)/download/$', views.download_dump, name="explorer_extensions.download_dump"),
    url(r'^export/(?P<dump_id>\d+)/delete/$', views.delete_dump, name="explorer_extensions.delete_dump"),
]
