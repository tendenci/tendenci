from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^payonline/(?P<payment_id>\d+)/(?P<guid>[\d\w-]+)/$', views.pay_online, name="square.payonline"),
    re_path(r'^thankyou/(?P<payment_id>\d+)/(?P<guid>[\d\w-]+)/$', views.thank_you, name="square.thank_you"),
    re_path(r'^update-card/(?P<rp_id>\d+)/$', views.update_card, name="square.update_card"),
    re_path(r'^giftcard/balance/$', views.ajax_giftcard_balance, name='square.gc_balance'),
    re_path(r'^card/charge/$', views.ajax_charge_card, name='square.card_charge'),
]

