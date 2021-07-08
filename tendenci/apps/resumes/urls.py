from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed

urlpath = get_setting('module', 'resumes', 'url')
if not urlpath:
    urlpath = "resumes"

urlpatterns = [
    re_path(r'^%s/$' % urlpath, views.search, name="resumes"),
    re_path(r'^%s/search/$' % urlpath, views.search_redirect, name="resume.search"),
    re_path(r'^%s/print-view/(?P<slug>[\w\-\/]+)/$' % urlpath, views.print_view, name="resume.print_view"),
    re_path(r'^%s/add/$' % urlpath, views.add, name="resume.add"),
    re_path(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="resume.edit"),
    re_path(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, views.edit_meta, name="resume.edit.meta"),
    re_path(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="resume.delete"),
    re_path(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='resume.feed'),
    re_path(r'^%s/pending/$' % urlpath, views.pending, name="resume.pending"),
    re_path(r'^%s/approve/(?P<id>\d+)/$' % urlpath, views.approve, name="resume.approve"),
    re_path(r'^%s/thank-you/$' % urlpath, views.thank_you, name="resume.thank_you"),
    re_path(r'^%s/export/$' % urlpath, views.export, name="resume.export"),
    re_path(r'^%s/(?P<slug>[\w\-\/]+)/file/$' % urlpath, views.resume_file, name="resume.resume_file"),
    re_path(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, views.index, name="resume"),
]
