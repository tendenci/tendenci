from django.conf.urls import patterns, url

urlpatterns = patterns('tendenci.apps.payments.payflowlink.views',
     url(r'^thankyou/$', 'thank_you', name="payflowlink.thank_you"),
     url(r'^silentpost/', 'silent_post', name="payflowlink.silent_post"),
)
