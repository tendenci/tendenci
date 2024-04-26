from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^(?P<ct>\d+)/(?P<object_id>\d+)/$', views.version_list, name="versions"),
]
