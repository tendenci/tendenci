from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^payonline/(?P<payment_id>\d+)/(?P<guid>[\d\w-]+)/$', views.pay_online, name="stripe.payonline"),
    url(r'^thankyou/(?P<payment_id>\d+)/(?P<guid>[\d\w-]+)/$', views.thank_you, name="stripe.thank_you"),
    url(r'^update-card/(?P<rp_id>\d+)/$', views.update_card, name="stripe.update_card"),
    url(r'^connect/authorize/$', views.AuthorizeView.as_view(), name="stripe_connect.authorize"),
    url(r'^connect/deauthorize/(?P<sa_id>\d+)/$', views.DeauthorizeView.as_view(), name="stripe_connect.deauthorize"),
    url(r'^connect/fetch-access-token/$', views.FetchAccessToken.as_view()),
    url(r'^connect/webhooks/$', views.WebhooksView.as_view(), name='stripe_connect.webhooks'),
]

