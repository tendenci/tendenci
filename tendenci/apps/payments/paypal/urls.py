from django.urls import path, re_path
from . import views

urlpatterns = [
     re_path(r'^thankyou/$', views.thank_you, name="paypal.thank_you"),
     re_path(r'^ipn/', views.ipn, name="paypal.ipn"),
]
