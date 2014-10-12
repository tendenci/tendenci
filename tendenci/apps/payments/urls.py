from django.conf.urls import patterns, url, include

urlpatterns = patterns('tendenci.apps.payments.views',
    url(r'^payonline/(?P<invoice_id>\d+)/(?P<guid>[\d\w-]+)?$', 'pay_online', name="payment.pay_online"),
    (r'^authorizenet/', include('tendenci.apps.payments.authorizenet.urls')),
    (r'^firstdata/', include('tendenci.apps.payments.firstdata.urls')),
    (r'^firstdatae4/', include('tendenci.apps.payments.firstdatae4.urls')),
    (r'^payflowlink/', include('tendenci.apps.payments.payflowlink.urls')),
    (r'^paypal/', include('tendenci.apps.payments.paypal.urls')),
    (r'^stripe/', include('tendenci.apps.payments.stripe.urls')),
    url(r'^(?P<id>\d+)/(?P<guid>[\d\w-]+)?$', 'view', name="payment.view"),
    url(r'^receipt/(?P<id>\d+)/(?P<guid>[\d\w-]+)$', 'receipt', name="payment.receipt"),
    url(r'^search/$', 'search', name='payment.search'),
)
