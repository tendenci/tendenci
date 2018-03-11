from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name="wp_exporter"),
    url(r'^detail/(?P<task_id>[-\w]+)/$', views.detail, name='export_detail'),
    url(r'^download/(?P<export_id>\d+)/$', views.download),
]
