from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^rp/$', views.api_rp),
]
