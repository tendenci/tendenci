from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^(?P<export_id>\d+)/$', views.status, name="export.status"),
    re_path(r'^(?P<export_id>\d+)/download/$', views.download, name="export.download"),
]
