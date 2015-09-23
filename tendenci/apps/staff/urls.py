from django.conf.urls import patterns, url
from tendenci.apps.staff.feeds import LatestEntriesFeed
from tendenci.apps.site_settings.utils import get_setting

urlpath = get_setting('module', 'staff', 'staff_url')
if not urlpath:
    urlpath = "staff"

urlpatterns = patterns('tendenci.apps.staff.views',
    url(r'^%s/$' % urlpath, 'search', name="staff"),
    url(r'^%s/search/$' % urlpath, 'search_redirect', name="staff.search"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='staff.feed'),
    url(r'^%s/(?P<slug>[\w\-]+)/$' % urlpath, 'detail', name="staff.view"),
    url(r'^%s/(?P<slug>[\w\-]+)/(?P<cv>cv)/$' % urlpath, 'detail', name="staff.cv"),
    #url(r'^%s/departments/(?P<department>\d+)/$' % urlpath, 'department_listing', name="staff.department_listing"),
)
