from django.conf.urls.defaults import patterns, url

from tendenci.core.files.signals import init_signals
from tendenci.core.site_settings.utils import get_setting


init_signals()

urlpath = get_setting('module', 'files', 'url')
if not urlpath:
    urlpath = "files"


urlpatterns = patterns('tendenci.core.files.views',
    url(r'^%s/$' % urlpath, 'search', name="files"),
    url(r'^%s/(?P<id>\d+)/$' % urlpath, 'details', name="file"),
    url(r'^%s/(?P<id>\d+)/(?P<download>(download)?)/$' % urlpath, 'details', name="file"),
    url(r'^%s/(?P<id>\d+)/(?P<size>\d*x\d*)/$' % urlpath, 'details', name="file"),
    url(r'^%s/(?P<id>\d+)/(?P<size>\d*x\d*)/(?P<constrain>constrain)/$' % urlpath, 'details', name="file"),
    url(r'^%s/(?P<id>\d+)/(?P<size>\d*x\d*)/(?P<constrain>constrain)/(?P<quality>\d+)/$' % urlpath, 'details', name="file"),
    url(r'^%s/(?P<id>\d+)/(?P<size>\d*x\d*)/(?P<download>download)/$' % urlpath, 'details', name="file"),
    url(r'^%s/(?P<id>\d+)/(?P<size>\d*x\d*)/(?P<download>download)/(?P<constrain>constrain)/$' % urlpath, 'details', name="file"),

    # crop and quality
    url(r'^%s/(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<crop>crop)/$' % urlpath, 'details', name="file"),
    url(r'^%s/(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<quality>\d+)/$' % urlpath, 'details', name="file"),
    url(r'^%s/(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<crop>crop)/(?P<quality>\d+)/$' % urlpath, 'details', name="file"),

    url(r'^%s/search/$' % urlpath, 'search_redirect', name="file.search"),
    url(r'^%s/add/$' % urlpath, 'add', name="file.add"),
    url(r'^%s/bulk-add/$' % urlpath, 'bulk_add', name="file.bulk_add"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, 'edit', name="file.edit"),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, 'delete', name="file.delete"),

    url(r'^%s/tinymce/$' % urlpath, 'tinymce', name="file.tinymce"),
    url(r'^%s/tinymce/get-files/$' % urlpath, 'tinymce_get_files', name="file.tinymce_get_files"),
    url(r'^%s/tinymce/template/(?P<id>\d+)/$' % urlpath, 'tinymce_upload_template'),
    url(r'^%s/swfupload/$' % urlpath, 'swfupload', name="file.swfupload"),

    url(r'^%s/reports/most-viewed/$' % urlpath, 'report_most_viewed', name="file.report_most_viewed"),

    url(r'^%s/get_categories/$' % urlpath, 'get_categories', name="file.get_categories"),
)
