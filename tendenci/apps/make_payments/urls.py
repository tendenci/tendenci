from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.add, name="make_payment.add"),
    url(r'^conf/(?P<id>\d+)/$', views.add_confirm, name="make_payment.add_confirm"),
    url(r'^(?P<id>\d+)/$', views.view, name="make_payment.view"),
]
