from django.conf.urls import url
from . import views

urlpatterns = [
     url(r'^thankyou/$', views.thank_you, name="paypal.thank_you"),
     url(r'^ipn/', views.ipn, name="paypal.ipn"),
]
