from django.urls import path, re_path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
     # re_path(r'^thankyou/(?P<payment_id>\d+)/(?P<guid>[\d\w-]+)/$', views.thank_you, name="authorizenet.thank_you"),
     # re_path(r'^silent-post/$', views.silent_post, name="authorizenet.silent_post"),
     re_path(r'^payonline/(?P<payment_id>\d+)/(?P<guid>[\d\w-]+)/$', views.pay_online, name="authorizenet.pay_online"),
     # re_path(r'^payonline-direct/(?P<payment_id>\d+)/(?P<guid>[\d\w-]+)/$', views.pay_online_direct, name="authorizenet.pay_online_direct"),
     re_path(r'^communicator/$', TemplateView.as_view(template_name='payments/authorizenet/iframe_communicator.html'),
        name='authorizenet.iframe_communicator'),
]
