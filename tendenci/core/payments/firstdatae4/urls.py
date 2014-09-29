from django.conf.urls.defaults import *

urlpatterns = patterns('tendenci.core.payments.firstdatae4.views',
     url(r'^thankyou/(?P<payment_id>\d+)/$', 'thank_you', name="firstdatae4_thank_you"),
     url(r'^silent-post/$', 'silent_post', name="firstdatae4.silent_post"),
)

