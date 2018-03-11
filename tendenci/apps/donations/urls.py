from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^donations/$', views.add, name="donation.add"),
    url(r'^donations/conf/(?P<id>\d+)/$', views.add_confirm, name="donation.add_confirm"),
    url(r'^donations/(?P<id>\d+)/$', views.detail, name="donation.view"),
    url(r'^donations/receipt/(?P<id>\d+)/(?P<guid>[\d\w-]+)/$', views.receipt, name="donation.receipt"),
    url(r'^donations/search/$', views.search, name="donation.search"),
]
