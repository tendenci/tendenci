from django.conf.urls.defaults import *

urlpatterns = patterns('tendenci.core.payments.payflowlink.views',
     url(r'^thankyou/$', 'thank_you', name="payflowlink.thank_you"),
     url(r'^silentpost/', 'silent_post', name="payflowlink.silent_post"),
)