from django.conf.urls.defaults import *

urlpatterns = patterns('payments.authorizenet.views',
     url(r'^thankyou/(?P<payment_id>\d+)/$', 'sim_thank_you', name="authorizenet.sim_thank_you"),
     #url(r'^thankyou/(?P<payment_id>\d+)/', 'sim_thank_you', name="authorizenet.sim_thank_you"),
)

