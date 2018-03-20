from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^image-preview/(?P<app_label>\w+)/(?P<model>\w+)/(?P<id>\d+)/(?P<size>(\d+|\d+x\d+))/$', views.image_preview, name="image_preview"),
    url(r'^feedback/$', views.feedback, name='tendenci_feedback'),
    url(r'^memcached-status/$', views.memcached_status, name='memcached_status'),
    url(r'^clear-cache/$', views.clear_cache, name='clear_cache'),
    url(r'^password_again/$', views.password_again, name="password_again"),
    url(r'^exception-test/$', views.exception_test, name="exception_test"),
    url(r'^timeout-test/$', views.timeout_test, name="timeout_test"),

    url(r'^checklist/$', views.checklist, name="completion_checklist"),

    url(r'^setlang/$', views.set_language, name="base.set_language"),

    url(r'^update-tendenci/$', views.update_tendenci, name="update_tendenci"),
    url(r'^update-tendenci/confirmation/$', views.update_tendenci_confirmation, name="update_tendenci.confirmation"),

    url(r'addon/upload/$', views.addon_upload, name="addon.upload"),
    url(r'addon/upload/preview/(?P<sid>\d+)$', views.addon_upload_preview, name="addon.upload.preview"),
    url(r'addon/upload/status/(?P<sid>\d+)$', views.addon_upload_process, name="addon.upload.process"),
    url(r'addon/upload/check/(?P<sid>\d+)$', views.addon_upload_check, name="addon.upload.check"),

    url(r'apps-list/$', login_required(views.AppsListView.as_view()), name="apps.list"),
]
