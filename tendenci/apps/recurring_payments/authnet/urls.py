from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('tendenci.addons.recurring_payments.authnet.views',
     url(r'^manage_payment_info/(?P<recurring_payment_id>\d+)/$', 'manage_payment_info',
         name="recurring_payment.authnet.manage_payment_info"),
     url(r'^update_payment_info/(?P<recurring_payment_id>\d+)/$', 'update_payment_info',
         name="recurring_payment.authnet.update_payment_info"),
    (r'^empty/$', direct_to_template, {'template': 'recurring_payments/authnet/empty.html'}),
     url(r'^iframe_communicator/$', direct_to_template,
         {'template': 'recurring_payments/authnet/IframeCommunicator.html'},
         name='recurring_payment.authnet.iframe_communicator'),
     url(r'^update_payment_profile_local/$', 'update_payment_profile_local',
         name="recurring_payment.authnet.update_payment_profile_local"),
     url(r'^retrieve_token/$', 'retrieve_token',
         name="recurring_payment.authnet.retrieve_token"),

)