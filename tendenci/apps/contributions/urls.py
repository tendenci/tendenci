from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tendenci.apps.contributions.views',
    url(r'^$', 'index', name="contribution"),
    url(r'^(?P<id>\d+)/$', 'index', name="contribution"),
    url(r'^search/$', 'search', name="contribution.search"),
)