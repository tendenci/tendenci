from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^(?P<ics_id>\d+)/$', views.status, name="ics.status"),
    re_path(r'^(?P<ics_id>\d+)/download/$', views.download, name="ics.download"),
]
