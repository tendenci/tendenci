from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('recurring_payments.authnet.views',
     url(r'^manage_payment_info/(?P<recurring_payment_id>\d+)/$', 'manage_payment_info', name="recurring_payment.authnet.manage_payment_info"),
     (r'^empty/$', direct_to_template, {'template': 'recurring_payments/authnet/empty.html'}),
)