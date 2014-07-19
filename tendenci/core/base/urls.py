from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tendenci.core.base.views',
    url(r'^image-preview/(?P<app_label>\w+)/(?P<model>\w+)/(?P<id>\d+)/(?P<size>(\d+|\d+x\d+))/$', 'image_preview', name="image_preview"),
    url(r'^feedback/$', 'feedback', name='tendenci_feedback'),
    url(r'^memcached-status/$', 'memcached_status', name='memcached_status'),
    url(r'^clear-cache/$', 'clear_cache', name='clear_cache'),
    url(r'^password_again/$', 'password_again', name="password_again"),
    url(r'^exception-test/$', 'exception_test', name="exception_test"),
    url(r'^timeout-test/$', 'timeout_test', name="timeout_test"),

    url(r'^checklist/$', 'checklist', name="completion_checklist"),
    
    url(r'^setlang/$', 'set_language', name="base.set_language"),

    url(r'^update-tendenci/$', 'update_tendenci', name="update_tendenci"),
    url(r'^update-tendenci/confirmation/$', 'update_tendenci_confirmation', name="update_tendenci.confirmation"),

    url(r'addon/upload/$', 'addon_upload', name="addon.upload"),
    url(r'addon/upload/preview/(?P<sid>\d+)$', 'addon_upload_preview', name="addon.upload.preview"),
    url(r'addon/upload/status/(?P<sid>\d+)$', 'addon_upload_process', name="addon.upload.process"),
    url(r'addon/upload/check/(?P<sid>\d+)$', 'addon_upload_check', name="addon.upload.check"),
)
