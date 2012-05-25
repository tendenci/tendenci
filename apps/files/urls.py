from django.conf.urls.defaults import patterns, url
from files.signals import init_signals


init_signals()

urlpatterns = patterns('files',                  
    url(r'^$', 'views.search', name="files"),
    url(r'^(?P<id>\d+)/$', 'views.details', name="file"),
    url(r'^(?P<id>\d+)/(?P<download>[download/]*)$', 'views.details', name="file"),
    url(r'^(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<download>[download/]*)$', 'views.details', name="file"),

    # crop and quality
    url(r'^(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<crop>[crop]*)/?$', 'views.details', name="file"),
    url(r'^(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<quality>\d+)/?$', 'views.details', name="file"),
    url(r'^(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<crop>[crop]*)/(?P<quality>\d+)/?$', 'views.details', name="file"),

    url(r'^search/$', 'views.search_redirect', name="file.search"),
    url(r'^add/$', 'views.add', name="file.add"),
    url(r'^edit/(?P<id>\d+)/$', 'views.edit', name="file.edit"),
    url(r'^delete/(?P<id>\d+)/$', 'views.delete', name="file.delete"),

    url(r'^tinymce/$', 'views.tinymce', name="file.tinymce"),
    url(r'^tinymce/template/(?P<id>\d+)/$', 'views.tinymce_upload_template'),
    url(r'^swfupload/$', 'views.swfupload', name="file.swfupload"),

    # url(r'^reports/$', 'views.reports', name="file.reports"),
    url(r'^reports/most-viewed/$', 'views.report_most_viewed', name="file.report_most_viewed"),
)