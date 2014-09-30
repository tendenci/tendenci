from django.conf.urls.defaults import *

urlpatterns = patterns('tendenci.core.payments.firstdatae4.views',
     url(r'^thankyou/$', 'thank_you', name="firstdatae4.thank_you"),
     url(r'^silent-post/$', 'silent_post', name="firstdatae4.silent_post"),
)

