from django.conf.urls.defaults import patterns, url
from feeds import LatestEntriesFeed
from site_settings.utils import get_setting

urlpath = get_setting('module', 'staff', 'staff_url')

urlpatterns = patterns('staff.views',
    url(r'^%s/$' % urlpath, 'index', name="staff"),
    url(r'^%s/search/$' % urlpath, 'search', name="staff.search"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='staff.feed'),
    url(r'^%s/(?P<slug>[\w\-]+)/$' % urlpath, 'index', name="staff.view"),
    url(r'^%s/(?P<slug>[\w\-]+)/(?P<cv>cv)/$' % urlpath, 'index', name="staff.cv"),
)
