from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.new, name="dashboard"),
    re_path(r'^new/$', views.new, name="dashboard-new"),
    re_path(r'^old/$', views.index, name="dashboard-old"),
    re_path(r'^customize/$', views.customize, name="dashboard_customize"),
]
