from django.conf.urls.defaults import *

urlpatterns = patterns('media_files.views', 
    url(r'^$', 'media_files', name="media_files"),
    url(r'^upload/$', 'media_file_upload', name="media_file_upload"),
    url(r'^delete/(?P<id>\d+)/$', 'media_file_delete', name="media_file_delete"),
    url(r'^tinymce/$', 'media_file_tinymce', name="media_file_tinymce"),
    url(r'^tinymce/proxy/checkDocument$', 'media_file_tinymce_proxy', name="media_file_tinymce_proxy"),
    url(r'^tinymce/template/image/$', 'media_file_template_image', name="media_file_template_image"),
)