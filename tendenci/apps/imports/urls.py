from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^users/upload/add/$', views.user_upload_add, name="import.user_upload_add"),
    re_path(r'^users/upload/preview/(?P<sid>\d+)$', views.user_upload_preview, name="import.user_upload_preview"),
    re_path(r'^users/upload/process/(?P<sid>\d+)$', views.user_upload_process, name="import.user_upload_process"),
    re_path(r'^users/upload/subprocess/(?P<sid>\d+)$', views.user_upload_subprocess, name="import.user_upload_subprocess"),
    re_path(r'^users/upload/recap/(?P<sid>\d+)$', views.user_upload_recap, name="import.user_upload_recap"),
    re_path(r'^users/upload/formats/$', views.download_user_upload_template, name="import.download_user_upload_template_xls"),
    re_path(r'^users/upload/formats/csv/$', views.download_user_upload_template, {'file_ext': '.csv'}, name="import.download_user_upload_template_csv"),
]
