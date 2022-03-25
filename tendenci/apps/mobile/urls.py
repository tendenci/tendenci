from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^toggle_mobile_mode/$', views.toggle_mobile_mode, name="toggle_mobile_mode"),
]
