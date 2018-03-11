from django.conf.urls import url
from tendenci.apps.files.signals import init_signals
from tendenci.apps.site_settings.utils import get_setting
from . import views

init_signals()

urlpath = get_setting('module', 'files', 'url')
if not urlpath:
    urlpath = "files"

urlpatterns = [
    url(r'^%s/$' % urlpath, views.search, name="files"),
    url(r'^%s/(?P<id>\d+)/$' % urlpath, views.details, name="file"),
    url(r'^%s/(?P<id>\d+)$' % urlpath, views.details, name="file_no_trailing_slash"),
    url(r'^%s/(?P<id>\d+)/(?P<download>(download)?)/$' % urlpath, views.details, name="file"),
    url(r'^%s/(?P<id>\d+)/(?P<size>\d*x\d*)/$' % urlpath, views.details, name="file"),
    url(r'^%s/(?P<id>\d+)/(?P<size>\d*x\d*)$' % urlpath, views.details, name="file_no_trailing_slash"),
    url(r'^%s/(?P<id>\d+)/(?P<size>\d*x\d*)/(?P<constrain>constrain)/$' % urlpath, views.details, name="file"),
    url(r'^%s/(?P<id>\d+)/(?P<size>\d*x\d*)/(?P<constrain>constrain)$' % urlpath, views.details, name="file_no_trailing_slash"),
    url(r'^%s/(?P<id>\d+)/(?P<size>\d*x\d*)/(?P<constrain>constrain)/(?P<quality>\d+)/$' % urlpath, views.details, name="file"),
    url(r'^%s/(?P<id>\d+)/(?P<size>\d*x\d*)/(?P<constrain>constrain)/(?P<quality>\d+)$' % urlpath, views.details, name="file_no_trailing_slash"),
    url(r'^%s/(?P<id>\d+)/(?P<size>\d*x\d*)/(?P<download>download)/$' % urlpath, views.details, name="file"),
    url(r'^%s/(?P<id>\d+)/(?P<size>\d*x\d*)/(?P<download>download)/(?P<constrain>constrain)/$' % urlpath, views.details, name="file"),

    # crop and quality
    url(r'^%s/(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<crop>crop)/$' % urlpath, views.details, name="file"),
    url(r'^%s/(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<crop>crop)$' % urlpath, views.details, name="file_no_trailing_slash"),
    url(r'^%s/(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<quality>\d+)/$' % urlpath, views.details, name="file"),
    url(r'^%s/(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<quality>\d+)$' % urlpath, views.details, name="file_no_trailing_slash"),
    url(r'^%s/(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<crop>crop)/(?P<quality>\d+)/$' % urlpath, views.details, name="file"),
    url(r'^%s/(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<crop>crop)/(?P<quality>\d+)$' % urlpath, views.details, name="file_no_trailing_slash"),

    url(r'^%s/search/$' % urlpath, views.search_redirect, name="file.search"),
    url(r'^%s/add/$' % urlpath, views.add, name="file.add"),
#     url(r'^%s/bulk-add/$' % urlpath, views.bulk_add, name="file.bulk_add"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="file.edit"),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="file.delete"),

    url(r'^%s/tinymce-fb/$' % urlpath, views.tinymce_fb, name="file.tinymce_fb"),
    url(r'^%s/tinymce/upload/$' % urlpath, views.FileTinymceCreateView.as_view(), name="file.tinymce_upload"),
    #url(r'^%s/tinymce/get-files/$' % urlpath, views.tinymce_get_files, name="file.tinymce_get_files"),
    #url(r'^%s/tinymce/template/(?P<id>\d+)/$' % urlpath, views.tinymce_upload_template),

    url(r'^%s/reports/most-viewed/$' % urlpath, views.report_most_viewed, name="file.report_most_viewed"),

    url(r'^%s/get_categories/$' % urlpath, views.get_categories, name="file.get_categories"),
]
