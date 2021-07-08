from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed

urlpath = get_setting('module', 'staff', 'staff_url')
if not urlpath:
    urlpath = "staff"

urlpatterns = [
    re_path(r'^%s/$' % urlpath, views.search, name="staff"),
    re_path(r'^%s/search/$' % urlpath, views.search_redirect, name="staff.search"),
    re_path(r'^%s/department/(?P<slug>[\w\-]+)/$' % urlpath, views.search, name="staff.department_view"),
    re_path(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='staff.feed'),
    re_path(r'^%s/(?P<slug>[\w\-]+)/$' % urlpath, views.detail, name="staff.view"),
    re_path(r'^%s/(?P<slug>[\w\-]+)/(?P<cv>cv)/$' % urlpath, views.detail, name="staff.cv"),
    #re_path(r'^%s/departments/(?P<department>\d+)/$' % urlpath, views.department_listing, name="staff.department_listing"),
]
