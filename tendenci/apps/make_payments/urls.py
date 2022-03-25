from django.urls import path, re_path
from . import views


urlpatterns = [
    re_path(r'^$', views.add, name="make_payment.add"),
    re_path(r'^conf/(?P<id>\d+)/$', views.add_confirm, name="make_payment.add_confirm"),
    re_path(r'^(?P<id>\d+)/$', views.view, name="make_payment.view"),
]
