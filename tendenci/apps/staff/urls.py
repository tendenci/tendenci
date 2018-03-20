from django.conf.urls import url
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed

urlpath = get_setting('module', 'staff', 'staff_url')
if not urlpath:
    urlpath = "staff"

urlpatterns = [
    url(r'^%s/$' % urlpath, views.search, name="staff"),
    url(r'^%s/search/$' % urlpath, views.search_redirect, name="staff.search"),
    url(r'^%s/department/(?P<slug>[\w\-]+)/$' % urlpath, views.search, name="staff.department_view"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='staff.feed'),
    url(r'^%s/(?P<slug>[\w\-]+)/$' % urlpath, views.detail, name="staff.view"),
    url(r'^%s/(?P<slug>[\w\-]+)/(?P<cv>cv)/$' % urlpath, views.detail, name="staff.cv"),
    #url(r'^%s/departments/(?P<department>\d+)/$' % urlpath, views.department_listing, name="staff.department_listing"),
]
