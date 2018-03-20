from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^payonline/(?P<payment_id>\d+)/$', views.pay_online, name="stripe.payonline"),
    url(r'^thankyou/(?P<payment_id>\d+)/$', views.thank_you, name="stripe.thank_you"),
    url(r'^update-card/(?P<rp_id>\d+)/$', views.update_card, name="stripe.update_card"),
]
