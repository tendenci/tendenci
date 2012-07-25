from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('tendenci.apps.api',
    url(r'^rp/$', 'views.api_rp'),
)


