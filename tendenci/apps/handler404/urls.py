from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tendenci.core.handler404.views',
    url(r'^reports/$', 'reports_404', name="reports-404-count"),
)
