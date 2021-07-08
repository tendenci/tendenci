from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^account_numbers/$', views.account_numbers,
        name="accounting.account_numbers"),
]
