from django.conf.urls import *

urlpatterns = patterns('tendenci.apps.payments.stripe.views',
    url(r'^payonline/(?P<payment_id>\d+)/$', 'pay_online', name="stripe.payonline"),
    url(r'^thankyou/(?P<payment_id>\d+)/$', 'thank_you', name="stripe.thank_you"),

)