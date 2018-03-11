from django.conf.urls import url
from . import views
from .feeds import LatestEntriesFeed

urlpatterns = [
    url(r'^study-groups/$', views.search, name="studygroups.search"),
    url(r'^study-groups/add/$', views.add, name='studygroups.add'),
    url(r'^study-groups/edit/(?P<id>\d+)/$', views.edit, name='studygroups.edit'),
    url(r'^study-groups/edit/meta/(?P<id>\d+)/$', views.edit_meta, name="studygroups.edit.meta"),
    url(r'^study-groups/delete/(?P<id>\d+)/$', views.delete, name='studygroups.delete'),
    url(r'^study-groups/feed/$', LatestEntriesFeed(), name='studygroups.feed'),
    url(r'^study-groups/(?P<slug>[\w\-\/]+)/$', views.detail, name="studygroups.detail"),
]
