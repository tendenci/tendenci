from django.conf.urls import *

urlpatterns = patterns('tendenci.apps.payments.firstdatae4.views',
     url(r'^thankyou/$', 'thank_you', name="firstdatae4.thank_you"),
     url(r'^silent-post/$', 'silent_post', name="firstdatae4.silent_post"),
)

