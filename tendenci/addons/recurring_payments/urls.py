from django.conf.urls.defaults import patterns, url, include


urlpatterns = patterns('tendenci.addons.recurring_payments.views',
    url(r'^$', 'my_accounts',
         name="recurring_payment.my_accounts"),
    (r'^authnet/', include('recurring_payments.authnet.urls')),
    url(r'^(?P<recurring_payment_id>\d+)/$', 'view_account',
         name="recurring_payment.view_account"),
    url(r'^disable/(?P<rp_id>\d+)/$', 'disable_account',
         name="recurring_payment.disable_account"),
    url(r'^run_now/$', 'run_now',
         name="recurring_payment.run_now"),
    url(r'^customers/$', 'customers',
         name="recurring_payment.customers"),
    url(r'^receipt/(?P<rp_id>\d+)/(?P<payment_transaction_id>\d+)/(?P<rp_guid>[\d\w-]+)?$',
        'transaction_receipt',
         name="recurring_payment.transaction_receipt"),
    url(r'^(?P<username>[+-.\w\d@]+)/$', 'my_accounts',
         name="recurring_payment.my_accounts"),

    #(r'^api/', include(rp_resource.urls)),
)
