from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('',                  
    (r'^authnet/', include('recurring_payments.authnet.urls')),
)