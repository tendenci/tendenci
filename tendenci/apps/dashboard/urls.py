from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tendenci.apps.dashboard',
    url(r'^$', 'views.index', name="dashboard"),
)