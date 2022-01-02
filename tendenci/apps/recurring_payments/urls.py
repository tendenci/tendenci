from django.urls import path, re_path, include
from tendenci.apps.recurring_payments.signals import init_signals
from . import views

init_signals()

urlpatterns = [
    re_path(r'^$', views.my_accounts,
         name="recurring_payment.my_accounts"),
    re_path(r'^authnet/', include('tendenci.apps.recurring_payments.authnet.urls')),
    re_path(r'^(?P<recurring_payment_id>\d+)/(?P<guid>[\d\w-]+)?$', views.view_account,
         name="recurring_payment.view_account"),
    re_path(r'^disable/(?P<rp_id>\d+)/$', views.disable_account,
         name="recurring_payment.disable_account"),
    re_path(r'^run_now/$', views.run_now,
         name="recurring_payment.run_now"),
    re_path(r'^customers/$', views.customers,
         name="recurring_payment.customers"),
    re_path(r'^receipt/(?P<rp_id>\d+)/(?P<payment_transaction_id>\d+)/(?P<rp_guid>[\d\w-]+)?$',
        views.transaction_receipt,
         name="recurring_payment.transaction_receipt"),
    re_path(r'^(?P<username>[+-.\w\d@]+)/$', views.my_accounts,
         name="recurring_payment.my_accounts"),

    #re_path(r'^api/', include(rp_resource.urls)),
]
