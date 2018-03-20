from django.conf.urls import url
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed

urlpath = get_setting('module', 'projects', 'url')
if not urlpath:
    urlpath = "projects"

urlpatterns = [
    url(r'^%s/$' % urlpath, views.index, name="projects"),
    url(r'^%s/search/$' % urlpath, views.search, name="projects.search"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='projects.feed'),
    url(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, views.detail, name="projects.detail"),
]
