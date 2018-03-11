from django.conf.urls import url, include
from tendenci.apps.recurring_payments.signals import init_signals
from . import views

init_signals()

urlpatterns = [
    url(r'^$', views.my_accounts,
         name="recurring_payment.my_accounts"),
    url(r'^authnet/', include('tendenci.apps.recurring_payments.authnet.urls')),
    url(r'^(?P<recurring_payment_id>\d+)/(?P<guid>[\d\w-]+)?$', views.view_account,
         name="recurring_payment.view_account"),
    url(r'^disable/(?P<rp_id>\d+)/$', views.disable_account,
         name="recurring_payment.disable_account"),
    url(r'^run_now/$', views.run_now,
         name="recurring_payment.run_now"),
    url(r'^customers/$', views.customers,
         name="recurring_payment.customers"),
    url(r'^receipt/(?P<rp_id>\d+)/(?P<payment_transaction_id>\d+)/(?P<rp_guid>[\d\w-]+)?$',
        views.transaction_receipt,
         name="recurring_payment.transaction_receipt"),
    url(r'^(?P<username>[+-.\w\d@]+)/$', views.my_accounts,
         name="recurring_payment.my_accounts"),

    #url(r'^api/', include(rp_resource.urls)),
]
