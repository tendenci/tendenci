from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
from . import views

urlpath = get_setting('module', 'donations', 'url') or 'donations'

urlpatterns = [
    re_path(fr'^{urlpath}/$', views.add, name="donation.add"),
    re_path(fr'^{urlpath}/conf/(?P<id>\d+)/(?P<guid>[\d\w-]+)/$', views.add_confirm, name="donation.add_confirm"),
    re_path(fr'^{urlpath}/(?P<id>\d+)/$', views.detail, name="donation.view"),
    re_path(fr'^{urlpath}/receipt/(?P<id>\d+)/(?P<guid>[\d\w-]+)/$', views.receipt, name="donation.receipt"),
    re_path(fr'^{urlpath}/search/$', views.search, name="donation.search"),
]
