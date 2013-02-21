from django.conf.urls.defaults import patterns, url

from tendenci.core.files.signals import init_signals


init_signals()

urlpatterns = patterns('tendenci.core.files.views',
    url(r'^$', 'search', name="files"),
    url(r'^(?P<id>\d+)/$', 'details', name="file"),
    url(r'^(?P<id>\d+)/(?P<download>(download)?)/$', 'details', name="file"),
    url(r'^(?P<id>\d+)/(?P<size>\d*x\d*)/$', 'details', name="file"),
    url(r'^(?P<id>\d+)/(?P<size>\d*x\d*)/(?P<constrain>constrain)/$', 'details', name="file"),
    url(r'^(?P<id>\d+)/(?P<size>\d*x\d*)/(?P<constrain>constrain)/(?P<quality>\d+)/$', 'details', name="file"),
    url(r'^(?P<id>\d+)/(?P<size>\d*x\d*)/(?P<download>download)/$', 'details', name="file"),
    url(r'^(?P<id>\d+)/(?P<size>\d*x\d*)/(?P<download>download)/(?P<constrain>constrain)/$', 'details', name="file"),

    # crop and quality
    url(r'^(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<crop>crop)/$', 'details', name="file"),
    url(r'^(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<quality>\d+)/$', 'details', name="file"),
    url(r'^(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<crop>crop)/(?P<quality>\d+)/$', 'details', name="file"),

    url(r'^search/$', 'search_redirect', name="file.search"),
    url(r'^add/$', 'add', name="file.add"),
    url(r'^bulk-add/$', 'bulk_add', name="file.bulk_add"),
    url(r'^edit/(?P<id>\d+)/$', 'edit', name="file.edit"),
    url(r'^delete/(?P<id>\d+)/$', 'delete', name="file.delete"),

    url(r'^tinymce/$', 'tinymce', name="file.tinymce"),
    url(r'^tinymce/template/(?P<id>\d+)/$', 'tinymce_upload_template'),
    url(r'^swfupload/$', 'swfupload', name="file.swfupload"),

    url(r'^reports/most-viewed/$', 'report_most_viewed', name="file.report_most_viewed"),
)
