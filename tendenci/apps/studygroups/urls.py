from django.conf.urls import patterns, url
from tendenci.apps.studygroups.feeds import LatestEntriesFeed

urlpatterns = patterns('tendenci.apps.studygroups.views',
    url(r'^study-groups/$', 'search', name="studygroups.search"),
    url(r'^study-groups/add/$', 'add', name='studygroups.add'),
    url(r'^study-groups/edit/(?P<id>\d+)/$', 'edit', name='studygroups.edit'),
    url(r'^study-groups/edit/meta/(?P<id>\d+)/$', 'edit_meta', name="studygroups.edit.meta"),
    url(r'^study-groups/delete/(?P<id>\d+)/$', 'delete', name='studygroups.delete'),
    url(r'^study-groups/feed/$', LatestEntriesFeed(), name='studygroups.feed'),
    url(r'^study-groups/(?P<slug>[\w\-\/]+)/$', 'detail', name="studygroups.detail"),
)
