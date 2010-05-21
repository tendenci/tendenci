from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',                  
    url(r'^(?P<scope>\w+)/(?P<scope_category>\w+)/$', 'site_settings.views.index', name="settings"),
)