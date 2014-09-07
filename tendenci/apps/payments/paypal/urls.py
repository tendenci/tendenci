from django.conf.urls import patterns, url

urlpatterns = patterns('tendenci.core.payments.paypal.views',
     url(r'^thankyou/$', 'thank_you', name="paypal.thank_you"),
     url(r'^ipn/', 'ipn', name="paypal.ipn"),
)
