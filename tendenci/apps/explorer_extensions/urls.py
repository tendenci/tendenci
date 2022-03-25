from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^export_database/$', views.export_page, name="explorer_extensions.export_page"),
    re_path(r'^export/(?P<dump_id>\d+)/download/$', views.download_dump, name="explorer_extensions.download_dump"),
    re_path(r'^export/(?P<dump_id>\d+)/delete/$', views.delete_dump, name="explorer_extensions.delete_dump"),
]
