from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^payonline/(?P<payment_id>\d+)/(?P<guid>[\d\w-]+)/$', views.pay_online, name="square.payonline"),
    url(r'^thankyou/(?P<payment_id>\d+)/(?P<guid>[\d\w-]+)/$', views.thank_you, name="square.thank_you"),
    url(r'^update-card/(?P<rp_id>\d+)/$', views.update_card, name="square.update_card"),
    url(r'^ajax/giftcard/balance/$', views.ajax_giftcard_balance, name='square.gc_balance'),
    url(r'^ajax/giftcard/charge/(?P<payment_id>\d+)/(?P<guid>[\d\w-]+)/$', views.ajax_charge_giftcard, name='square.gc_charge'),
]

