from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tendenci.contrib.dashboard',
    url(r'^$', 'views.index', name="dashboard"),
)