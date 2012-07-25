from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tendenci.apps.reports.views',
    url(r'^$', 'index', name="reports"),
)