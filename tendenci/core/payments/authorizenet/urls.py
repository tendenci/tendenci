from django.conf.urls.defaults import *

urlpatterns = patterns('tendenci.core.payments.authorizenet.views',
     url(r'^thankyou/(?P<payment_id>\d+)/$', 'sim_thank_you', name="authorizenet.sim_thank_you"),
     url(r'^silent-post/$', 'silent_post', name="authorizenet.silent_post"),
)

