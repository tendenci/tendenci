from django.urls import path, re_path
from . import views

urlpatterns = [
     re_path(r'^thankyou/$', views.thank_you, name="firstdatae4.thank_you"),
     re_path(r'^silent-post/$', views.silent_post, name="firstdatae4.silent_post"),
]
