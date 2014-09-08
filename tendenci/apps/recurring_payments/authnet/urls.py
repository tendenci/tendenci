from django.conf.urls import *
from django.views.generic import TemplateView

urlpatterns = patterns('tendenci.apps.recurring_payments.authnet.views',
     url(r'^manage_payment_info/(?P<recurring_payment_id>\d+)/$', 'manage_payment_info',
         name="recurring_payment.authnet.manage_payment_info"),
     url(r'^update_payment_info/(?P<recurring_payment_id>\d+)/$', 'update_payment_info',
         name="recurring_payment.authnet.update_payment_info"),
    (r'^empty/$', TemplateView.as_view(template_name='recurring_payments/authnet/empty.html')),
     url(r'^iframe_communicator/$', TemplateView.as_view(template_name='recurring_payments/authnet/IframeCommunicator.html'),
         name='recurring_payment.authnet.iframe_communicator'),
     url(r'^update_payment_profile_local/$', 'update_payment_profile_local',
         name="recurring_payment.authnet.update_payment_profile_local"),
     url(r'^retrieve_token/$', 'retrieve_token',
         name="recurring_payment.authnet.retrieve_token"),

)