from django.conf.urls import patterns, url

urlpatterns = patterns('tendenci.apps.api',
    url(r'^rp/$', 'views.api_rp'),
)
