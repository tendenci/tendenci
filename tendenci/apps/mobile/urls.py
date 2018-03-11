from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^toggle_mobile_mode/$', views.toggle_mobile_mode, name="toggle_mobile_mode"),
]
