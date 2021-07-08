from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^donations/$', views.add, name="donation.add"),
    re_path(r'^donations/conf/(?P<id>\d+)/$', views.add_confirm, name="donation.add_confirm"),
    re_path(r'^donations/(?P<id>\d+)/$', views.detail, name="donation.view"),
    re_path(r'^donations/receipt/(?P<id>\d+)/(?P<guid>[\d\w-]+)/$', views.receipt, name="donation.receipt"),
    re_path(r'^donations/search/$', views.search, name="donation.search"),
]
