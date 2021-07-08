from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^export/$', views.export, name='boxes.export'),
]
