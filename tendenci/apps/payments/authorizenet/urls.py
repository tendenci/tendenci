from django.conf.urls import url
from . import views

urlpatterns = [
     url(r'^thankyou/(?P<payment_id>\d+)/$', views.sim_thank_you, name="authorizenet.sim_thank_you"),
     url(r'^silent-post/$', views.silent_post, name="authorizenet.silent_post"),
]
