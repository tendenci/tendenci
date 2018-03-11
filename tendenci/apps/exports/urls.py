from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<export_id>\d+)/$', views.status, name="export.status"),
    url(r'^(?P<export_id>\d+)/download/$', views.download, name="export.download"),
]
