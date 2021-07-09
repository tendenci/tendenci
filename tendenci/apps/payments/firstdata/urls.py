from django.urls import path, re_path
from . import views

urlpatterns = [
     re_path(r'^thankyou/(?P<payment_id>\d+)/$', views.thank_you, name="firstdata.thank_you"),
     #re_path(r'^sorry/(?P<payment_id>\d+)/', views.sorry, name="authorizenet.sim_thank_you"),
]
