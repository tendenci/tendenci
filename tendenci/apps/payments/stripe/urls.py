from django.conf.urls.defaults import *

urlpatterns = patterns('tendenci.core.payments.stripe.views',
    url(r'^payonline/(?P<payment_id>\d+)/$', 'pay_online', name="stripe.payonline"),
    url(r'^thankyou/(?P<payment_id>\d+)/$', 'thank_you', name="stripe.thank_you"),

)