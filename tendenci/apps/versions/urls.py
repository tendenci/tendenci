from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<ct>\d+)/(?P<object_id>\d+)/$', views.version_list, name="versions"),
]
