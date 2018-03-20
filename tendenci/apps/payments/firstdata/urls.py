from django.conf.urls import url
from . import views

urlpatterns = [
     url(r'^thankyou/(?P<payment_id>\d+)/$', views.thank_you, name="firstdata.thank_you"),
     #url(r'^sorry/(?P<payment_id>\d+)/', views.sorry, name="authorizenet.sim_thank_you"),
]
