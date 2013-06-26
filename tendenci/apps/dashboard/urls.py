from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tendenci.apps.dashboard',
    url(r'^$', 'views.index', name="dashboard"),
    url(r'^new/$', 'views.new', name="dashboard-new"),
    url(r'^customize/$', 'views.customize', name="dashboard_customize"),
)
