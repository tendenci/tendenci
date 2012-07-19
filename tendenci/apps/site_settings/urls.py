from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('', 
    url(r'^$', 'site_settings.views.index', name="settings"),
    url(r'^(?P<scope>\w+)/(?P<scope_category>\w+)/$', 'site_settings.views.list', name="settings.index"),
    url(r'^(?P<scope>\w+)/(?P<scope_category>\w+)/(?P<name>\w+)/$', 'site_settings.views.single_setting', name="settings.single_setting"),
    url(r'^(?P<scope>\w+)/(?P<scope_category>\w+)/([#\w]+)$', 'site_settings.views.list', name="setting.permalink"),
)