from django.conf.urls import patterns, url

urlpatterns = patterns('tendenci.apps.site_settings.views',
    url(r'^$', 'index', name="settings"),
    url(r'^(?P<scope>\w+)/(?P<scope_category>\w+)/$', 'list', name="settings.index"),
    url(r'^(?P<scope>\w+)/(?P<scope_category>\w+)/(?P<name>\w+)/$', 'single_setting', name="settings.single_setting"),
    #url(r'^(?P<scope>\w+)/(?P<scope_category>\w+)/([#\w]+)$', 'list', name="setting.permalink"),
    url(r'^(?P<scope>\w+)/(?P<scope_category>\w+)/#id_(\w+)$', 'list', name="setting.permalink"),
)
