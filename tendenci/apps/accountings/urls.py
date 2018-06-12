from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^account_numbers/$', views.account_numbers,
        name="accounting.account_numbers"),
]
