from django.conf.urls.defaults import patterns, url
from chamberlin_projects.feeds import LatestEntriesFeed
from site_settings.utils import get_setting

urlpath = get_setting('module', 'chamberlin_projects', 'url')
if not urlpath:
    urlpath = "projects"

urlpatterns = patterns('chamberlin_projects.views',
    url(r'^%s/$' % urlpath, 'index', name="chamberlin_projects"),
    url(r'^%s/search/$' % urlpath, 'search', name="chamberlin_projects.search"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='chamberlin_projects.feed'),
    url(r'^%s/(?P<category>[\w\-]+)/$' % urlpath, 'category', name="chamberlin_projects.category"),
    url(r'^%s/(?P<category>[\w\-]+)/(?P<slug>[\w\-]+)/$' % urlpath, 'detail', name="chamberlin_projects.detail"),
)