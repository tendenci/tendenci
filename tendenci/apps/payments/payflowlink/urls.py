from django.urls import path, re_path
from . import views

urlpatterns = [
     re_path(r'^thankyou/$', views.thank_you, name="payflowlink.thank_you"),
     re_path(r'^silentpost/', views.silent_post, name="payflowlink.silent_post"),
]
