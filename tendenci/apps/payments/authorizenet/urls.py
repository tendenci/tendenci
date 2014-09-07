from django.conf.urls import *

urlpatterns = patterns('tendenci.apps.payments.authorizenet.views',
     url(r'^thankyou/(?P<payment_id>\d+)/$', 'sim_thank_you', name="authorizenet.sim_thank_you"),
     url(r'^silent-post/$', 'silent_post', name="authorizenet.silent_post"),
)

