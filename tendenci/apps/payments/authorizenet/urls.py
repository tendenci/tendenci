from django.urls import path, re_path
from . import views

urlpatterns = [
     re_path(r'^thankyou/(?P<payment_id>\d+)/$', views.sim_thank_you, name="authorizenet.sim_thank_you"),
     re_path(r'^silent-post/$', views.silent_post, name="authorizenet.silent_post"),
]
