from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<ics_id>\d+)/$', views.status, name="ics.status"),
    url(r'^(?P<ics_id>\d+)/download/$', views.download, name="ics.download"),
]
