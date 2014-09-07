from django.conf.urls import *

urlpatterns = patterns('tendenci.apps.payments.firstdata.views',
     url(r'^thankyou/(?P<payment_id>\d+)/$', 'thank_you', name="firstdata.thank_you"),
     #url(r'^sorry/(?P<payment_id>\d+)/', 'sorry', name="authorizenet.sim_thank_you"),
)