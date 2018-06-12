from django.conf.urls import patterns, url
from views import AuthorizeView, FetchAccessToken, DeauthorizeView, WebhooksView

urlpatterns = patterns('tendenci.apps.payments.stripe.views',
    url(r'^payonline/(?P<payment_id>\d+)/$', 'pay_online', name="stripe.payonline"),
    url(r'^thankyou/(?P<payment_id>\d+)/$', 'thank_you', name="stripe.thank_you"),
    url(r'^update-card/(?P<rp_id>\d+)/$', 'update_card', name="stripe.update_card"),
    url(r'^connect/authorize/$', AuthorizeView.as_view(), name="stripe_connect.authorize"),
    url(r'^connect/deauthorize/(?P<sa_id>\d+)/$', DeauthorizeView.as_view(), name="stripe_connect.deauthorize"),
    url(r'^connect/fetch-access-token/$', FetchAccessToken.as_view()),
    url(r'^connect/webhooks/$', WebhooksView.as_view(), name='stripe_connect.webhooks'),
)
