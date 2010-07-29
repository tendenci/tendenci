from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('imports.views', 
    url(r'^users/upload/add/$', 'user_upload_add', name="import.user_upload_add"),
    url(r'^users/upload/preview/$', 'user_upload_preview', name="import.user_upload_preview"),
    url(r'^users/upload/formats/$', 'download_user_upload_template_xls', name="import.download_user_formats"),
)