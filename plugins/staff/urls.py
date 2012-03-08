from django.conf.urls.defaults import patterns, url
from feeds import LatestEntriesFeed
from site_settings.utils import get_setting

urlpath = get_setting('module', 'staff', 'staff_url')
if not urlpath:
    urlpath = "staff"

urlpatterns = patterns('staff.views',
    url(r'^%s/$' % urlpath, 'search', name="staff"),
    url(r'^%s/search/$' % urlpath, 'search_redirect', name="staff.search"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='staff.feed'),
    url(r'^%s/(?P<slug>[\w\-]+)/$' % urlpath, 'details', name="staff.view"),
    url(r'^%s/(?P<slug>[\w\-]+)/(?P<cv>cv)/$' % urlpath, 'details', name="staff.cv"),
)
