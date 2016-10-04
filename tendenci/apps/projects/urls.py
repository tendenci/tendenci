from django.conf.urls import patterns, url
from tendenci.apps.projects.feeds import LatestEntriesFeed
from tendenci.apps.site_settings.utils import get_setting

urlpath = get_setting('module', 'projects', 'url')
if not urlpath:
    urlpath = "projects"

urlpatterns = patterns('tendenci.apps.projects.views',
    url(r'^%s/$' % urlpath, 'index', name="projects"),
    url(r'^%s/search/$' % urlpath, 'search', name="projects.search"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='projects.feed'),
    url(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, 'detail', name="projects.detail"),
)
