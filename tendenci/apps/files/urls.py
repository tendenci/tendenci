from django.urls import path, re_path
from tendenci.apps.files.signals import init_signals
from tendenci.apps.site_settings.utils import get_setting
from . import views

init_signals()

urlpath = get_setting('module', 'files', 'url')
if not urlpath:
    urlpath = "files"

urlpatterns = [
    re_path(r'^%s/$' % urlpath, views.search, name="files"),
    re_path(r'^%s/(?P<id>\d+)/$' % urlpath, views.details, name="file"),
    re_path(r'^%s/(?P<id>\d+)$' % urlpath, views.details, name="file_no_trailing_slash"),
    re_path(r'^%s/(?P<id>\d+)/(?P<download>(download)?)/$' % urlpath, views.details, name="file"),
    re_path(r'^%s/(?P<id>\d+)/(?P<size>\d*x\d*)/$' % urlpath, views.details, name="file"),
    re_path(r'^%s/(?P<id>\d+)/(?P<size>\d*x\d*)$' % urlpath, views.details, name="file_no_trailing_slash"),
    re_path(r'^%s/(?P<id>\d+)/(?P<size>\d*x\d*)/(?P<constrain>constrain)/$' % urlpath, views.details, name="file"),
    re_path(r'^%s/(?P<id>\d+)/(?P<size>\d*x\d*)/(?P<constrain>constrain)$' % urlpath, views.details, name="file_no_trailing_slash"),
    re_path(r'^%s/(?P<id>\d+)/(?P<size>\d*x\d*)/(?P<constrain>constrain)/(?P<quality>\d+)/$' % urlpath, views.details, name="file"),
    re_path(r'^%s/(?P<id>\d+)/(?P<size>\d*x\d*)/(?P<constrain>constrain)/(?P<quality>\d+)$' % urlpath, views.details, name="file_no_trailing_slash"),
    re_path(r'^%s/(?P<id>\d+)/(?P<size>\d*x\d*)/(?P<download>download)/$' % urlpath, views.details, name="file"),
    re_path(r'^%s/(?P<id>\d+)/(?P<size>\d*x\d*)/(?P<download>download)/(?P<constrain>constrain)/$' % urlpath, views.details, name="file"),

    # crop and quality
    re_path(r'^%s/(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<crop>crop)/$' % urlpath, views.details, name="file"),
    re_path(r'^%s/(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<crop>crop)$' % urlpath, views.details, name="file_no_trailing_slash"),
    re_path(r'^%s/(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<quality>\d+)/$' % urlpath, views.details, name="file"),
    re_path(r'^%s/(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<quality>\d+)$' % urlpath, views.details, name="file_no_trailing_slash"),
    re_path(r'^%s/(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<crop>crop)/(?P<quality>\d+)/$' % urlpath, views.details, name="file"),
    re_path(r'^%s/(?P<id>\d+)/(?P<size>\d+x\d+)/(?P<crop>crop)/(?P<quality>\d+)$' % urlpath, views.details, name="file_no_trailing_slash"),

    re_path(r'^%s/search/$' % urlpath, views.search_redirect, name="file.search"),
    re_path(r'^%s/add/$' % urlpath, views.add, name="file.add"),
#     re_path(r'^%s/bulk-add/$' % urlpath, views.bulk_add, name="file.bulk_add"),
    re_path(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="file.edit"),
    re_path(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="file.delete"),

    re_path(r'^%s/tinymce-fb/$' % urlpath, views.tinymce_fb, name="file.tinymce_fb"),
    re_path(r'^%s/tinymce/upload/$' % urlpath, views.FileTinymceCreateView.as_view(), name="file.tinymce_upload"),
    #re_path(r'^%s/tinymce/get-files/$' % urlpath, views.tinymce_get_files, name="file.tinymce_get_files"),
    #re_path(r'^%s/tinymce/template/(?P<id>\d+)/$' % urlpath, views.tinymce_upload_template),

    re_path(r'^%s/reports/most-viewed/$' % urlpath, views.report_most_viewed, name="file.report_most_viewed"),

    re_path(r'^%s/get_categories/$' % urlpath, views.get_categories, name="file.get_categories"),
]
