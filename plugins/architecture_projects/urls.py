from django.conf.urls.defaults import patterns, url
from feeds import LatestEntriesFeed

urlpatterns = patterns('architecture_projects.views',
    url(r'^architecture-projects/$', 'index', name="architecture_project"),
    url(r'^architecture-projects/search/$', 'search', name="architecture_project.search"),
    url(r'^architecture-projects/feed/$', LatestEntriesFeed(), name='architecture_project.feed'),
    url(r'^architecture-projects/(?P<slug>[\w\-]+)/$', 'index', name="architecture_project.view"),
    url(r'^architecture-projects/building_type/(?P<id>\d+)/$', 'building_type', name="architecture_project.building_type"),
    url(r'^architecture-projects/category/(?P<id>\d+)/$', 'category', name="architecture_project.category"),
)