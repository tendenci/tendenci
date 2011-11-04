from django.conf.urls.defaults import patterns, url, include

#from recurring_payments.api import RPResource
#rp_resource = RPResource()

urlpatterns = patterns('recurring_payments',                  
    (r'^authnet/', include('recurring_payments.authnet.urls')),
    url(r'^(?P<recurring_payment_id>\d+)/$', 'views.view_account', 
         name="recurring_payment.view_account"),
    url(r'^customers/$', 'views.customers', 
         name="recurring_payment.customers"),
    url(r'^receipt/(?P<rp_id>\d+)/(?P<payment_transaction_id>\d+)/(?P<rp_guid>[\d\w-]+)?$', 
        'views.transaction_receipt', 
         name="recurring_payment.transaction_receipt"),
                       
    #(r'^api/', include(rp_resource.urls)),
)