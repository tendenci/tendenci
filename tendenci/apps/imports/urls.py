from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^users/upload/add/$', views.user_upload_add, name="import.user_upload_add"),
    url(r'^users/upload/preview/(?P<sid>\d+)$', views.user_upload_preview, name="import.user_upload_preview"),
    url(r'^users/upload/process/(?P<sid>\d+)$', views.user_upload_process, name="import.user_upload_process"),
    url(r'^users/upload/subprocess/(?P<sid>\d+)$', views.user_upload_subprocess, name="import.user_upload_subprocess"),
    url(r'^users/upload/recap/(?P<sid>\d+)$', views.user_upload_recap, name="import.user_upload_recap"),
    url(r'^users/upload/formats/$', views.download_user_upload_template, name="import.download_user_upload_template_xls"),
    url(r'^users/upload/formats/csv/$', views.download_user_upload_template, {'file_ext': '.csv'}, name="import.download_user_upload_template_csv"),
]
