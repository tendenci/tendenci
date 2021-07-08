from django.urls import path, re_path, include
from . import views

urlpatterns = [
    re_path(r'^payonline/(?P<merchant_account>[\d\w-]+)/(?P<invoice_id>\d+)/(?P<guid>[\d\w-]+)?$', views.pay_online, name="payment.pay_online"),
    re_path(r'^payonline/(?P<invoice_id>\d+)/(?P<guid>[\d\w-]+)?$', views.pay_online, name="payment.pay_online"),
    re_path(r'^authorizenet/', include('tendenci.apps.payments.authorizenet.urls')),
    re_path(r'^firstdata/', include('tendenci.apps.payments.firstdata.urls')),
    re_path(r'^firstdatae4/', include('tendenci.apps.payments.firstdatae4.urls')),
    re_path(r'^payflowlink/', include('tendenci.apps.payments.payflowlink.urls')),
    re_path(r'^paypal/', include('tendenci.apps.payments.paypal.urls')),
    re_path(r'^stripe/', include('tendenci.apps.payments.stripe.urls')),
    re_path(r'^(?P<id>\d+)/(?P<guid>[\d\w-]+)?$', views.view, name="payment.view"),
    re_path(r'^receipt/(?P<id>\d+)/(?P<guid>[\d\w-]+)$', views.receipt, name="payment.receipt"),
    re_path(r'^search/$', views.search, name='payment.search'),
]
