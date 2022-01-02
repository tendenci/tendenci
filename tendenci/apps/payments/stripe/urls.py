from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^payonline/(?P<payment_id>\d+)/(?P<guid>[\d\w-]+)/$', views.pay_online, name="stripe.payonline"),
    re_path(r'^thankyou/(?P<payment_id>\d+)/(?P<guid>[\d\w-]+)/$', views.thank_you, name="stripe.thank_you"),
    re_path(r'^update-card/(?P<rp_id>\d+)/$', views.update_card, name="stripe.update_card"),
    re_path(r'^connect/authorize/$', views.AuthorizeView.as_view(), name="stripe_connect.authorize"),
    re_path(r'^connect/deauthorize/(?P<sa_id>\d+)/$', views.DeauthorizeView.as_view(), name="stripe_connect.deauthorize"),
    re_path(r'^connect/fetch-access-token/$', views.FetchAccessToken.as_view()),
    re_path(r'^connect/webhooks/$', views.WebhooksView.as_view(), name='stripe_connect.webhooks'),
]

