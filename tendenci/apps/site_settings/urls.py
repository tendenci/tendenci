from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tendenci.core.site_settings.views',
    url(r'^$', 'index', name="settings"),
    url(r'^(?P<scope>\w+)/(?P<scope_category>\w+)/$', 'list', name="settings.index"),
    url(r'^(?P<scope>\w+)/(?P<scope_category>\w+)/(?P<name>\w+)/$', 'single_setting', name="settings.single_setting"),
    url(r'^(?P<scope>\w+)/(?P<scope_category>\w+)/([#\w]+)$', 'list', name="setting.permalink"),
)
