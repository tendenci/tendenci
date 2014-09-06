from django.conf.urls.defaults import *

urlpatterns = patterns('tendenci.core.payments.firstdata.views',
     url(r'^thankyou/(?P<payment_id>\d+)/$', 'thank_you', name="firstdata.thank_you"),
     #url(r'^sorry/(?P<payment_id>\d+)/', 'sorry', name="authorizenet.sim_thank_you"),
)