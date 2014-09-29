from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('tendenci.core.payments.views',
    url(r'^payonline/(?P<invoice_id>\d+)/(?P<guid>[\d\w-]+)?$', 'pay_online', name="payment.pay_online"),
    (r'^authorizenet/', include('tendenci.core.payments.authorizenet.urls')),
    (r'^firstdata/', include('tendenci.core.payments.firstdata.urls')),
    (r'^firstdatae4/', include('tendenci.core.payments.firstdatae4.urls')),
    (r'^payflowlink/', include('tendenci.core.payments.payflowlink.urls')),
    (r'^paypal/', include('tendenci.core.payments.paypal.urls')),
    (r'^stripe/', include('tendenci.core.payments.stripe.urls')),
    url(r'^(?P<id>\d+)/(?P<guid>[\d\w-]+)?$', 'view', name="payment.view"),
    url(r'^receipt/(?P<id>\d+)/(?P<guid>[\d\w-]+)$', 'receipt', name="payment.receipt"),
    url(r'^search/$', 'search', name='payment.search'),
)
