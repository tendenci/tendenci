from django.conf.urls.defaults import patterns, url
from trainings.feeds import LatestEntriesFeed

urlpatterns = patterns('trainings.views',
    url(r'^trainings/$', 'search', name="trainings"),
    url(r'^trainings/search/$', 'search_redirect', name="trainings.search"),
    url(r'^trainings/feed/$', LatestEntriesFeed(), name='trainings.feed'),
    url(r'^trainings/(?P<pk>[\d/]+)/$', 'detail', name="trainings.detail"),
    url(r'^trainings/(?P<training_pk>[\d/]+)/complete/$', 'completion_add', name="trainings.completion_add"),
    url(r'^trainings/completion/edit/(?P<completion_pk>[\d/]+)/$', 'completion_edit', name="trainings.completion_edit"),
    url(r'^trainings/completion/delete/(?P<completion_pk>[\d/]+)/$', 'completion_delete', name="trainings.completion_delete"),
    url(r'^trainings/reports/all-completions/$', 'completion_report_all', name="trainings.completion_report_all"),
)