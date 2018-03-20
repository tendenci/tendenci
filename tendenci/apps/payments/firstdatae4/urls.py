from django.conf.urls import url
from . import views

urlpatterns = [
     url(r'^thankyou/$', views.thank_you, name="firstdatae4.thank_you"),
     url(r'^silent-post/$', views.silent_post, name="firstdatae4.silent_post"),
]
