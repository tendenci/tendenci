from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
from . import views

urlpatterns = [
    re_path(r'^request/(?P<to_directory_id>\d+)/$',
        views.request_associate, name="affiliates.request_associate"),
    re_path(r'^approve/(?P<affiliate_request_id>\d+)/$',
        views.approve, name="affiliates.request_approve"),
    re_path(r'^reject/(?P<affiliate_request_id>\d+)/$',
        views.reject, name="affiliates.request_reject"),
    re_path(r'^cancel/(?P<affiliate_request_id>\d+)/$',
        views.cancel, name="affiliates.request_cancel"),
    re_path(r'^delete/(?P<directory_id>\d+)/(?P<affiliate_id>\d+)/$',
        views.delete_affiliate, name="affiliates.delete_affiliate"),
    re_path(r'^requests-list/(?P<directory_id>\d+)/$',
        views.requests_list, name="affiliates.requests_list"),
]
