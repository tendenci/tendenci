from django.conf.urls.defaults import patterns, url
from files.signals import init_signals


init_signals()

urlpatterns = patterns('files',                  
    url(r'^$', 'views.index', name="files"),
    url(r'^(?P<id>\d+)/$', 'views.index', name="file"),
    url(r'^(?P<id>\d+)/(?P<download>[download/]*)$', 'views.index', name="file"),
    url(r'^(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<download>[download/]*)$', 'views.index', name="file"),

    url(r'^search/$', 'views.search', name="file.search"),
    url(r'^add/$', 'views.add', name="file.add"),
    url(r'^edit/(?P<id>\d+)/$', 'views.edit', name="file.edit"),
    url(r'^delete/(?P<id>\d+)/$', 'views.delete', name="file.delete"),

    url(r'^tinymce/$', 'views.tinymce', name="file.tinymce"),
    url(r'^tinymce/template/(?P<id>\d+)/$', 'views.tinymce_upload_template'),
    url(r'^swfupload/$', 'views.swfupload', name="file.swfupload"),
)