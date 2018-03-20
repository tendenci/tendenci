from django.conf.urls import url
from . import views

urlpatterns = [
     url(r'^thankyou/$', views.thank_you, name="payflowlink.thank_you"),
     url(r'^silentpost/', views.silent_post, name="payflowlink.silent_post"),
]
