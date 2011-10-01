from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('api',                  
    url(r'^rp/$', 'views.api_rp'),
)


