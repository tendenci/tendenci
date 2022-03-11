from django.urls import path, re_path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    re_path(r'^image-preview/(?P<app_label>\w+)/(?P<model>\w+)/(?P<id>\d+)/(?P<size>(\d+|\d+x\d+))/$', views.image_preview, name="image_preview"),
    re_path(r'^feedback/$', views.feedback, name='tendenci_feedback'),
    re_path(r'^memcached-status/$', views.memcached_status, name='memcached_status'),
    re_path(r'^clear-cache/$', views.clear_cache, name='clear_cache'),
    re_path(r'^password_again/$', views.password_again, name="password_again"),
    re_path(r'^exception-test/$', views.exception_test, name="exception_test"),
    re_path(r'^timeout-test/$', views.timeout_test, name="timeout_test"),

    re_path(r'^checklist/$', views.checklist, name="completion_checklist"),

    re_path(r'^setlang/$', views.set_language, name="base.set_language"),

    re_path(r'^update-tendenci/$', views.update_tendenci, name="update_tendenci"),
    re_path(r'^update-tendenci/confirmation/$', views.update_tendenci_confirmation, name="update_tendenci.confirmation"),

    re_path(r'addon/upload/$', views.addon_upload, name="addon.upload"),
    re_path(r'addon/upload/preview/(?P<sid>\d+)$', views.addon_upload_preview, name="addon.upload.preview"),
    re_path(r'addon/upload/status/(?P<sid>\d+)$', views.addon_upload_process, name="addon.upload.process"),
    re_path(r'addon/upload/check/(?P<sid>\d+)$', views.addon_upload_check, name="addon.upload.check"),

    re_path(r'apps-list/$', login_required(views.AppsListView.as_view()), name="apps.list"),
]
