from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^payonline/(?P<merchant_account>[\d\w-]+)/(?P<invoice_id>\d+)/(?P<guid>[\d\w-]+)?$', views.pay_online, name="payment.pay_online"),
    url(r'^payonline/(?P<invoice_id>\d+)/(?P<guid>[\d\w-]+)?$', views.pay_online, name="payment.pay_online"),
    url(r'^authorizenet/', include('tendenci.apps.payments.authorizenet.urls')),
    url(r'^firstdata/', include('tendenci.apps.payments.firstdata.urls')),
    url(r'^firstdatae4/', include('tendenci.apps.payments.firstdatae4.urls')),
    url(r'^payflowlink/', include('tendenci.apps.payments.payflowlink.urls')),
    url(r'^paypal/', include('tendenci.apps.payments.paypal.urls')),
    url(r'^stripe/', include('tendenci.apps.payments.stripe.urls')),
    url(r'^(?P<id>\d+)/(?P<guid>[\d\w-]+)?$', views.view, name="payment.view"),
    url(r'^receipt/(?P<id>\d+)/(?P<guid>[\d\w-]+)$', views.receipt, name="payment.receipt"),
    url(r'^search/$', views.search, name='payment.search'),
]
