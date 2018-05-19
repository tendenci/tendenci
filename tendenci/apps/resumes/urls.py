from django.conf.urls import url
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed

urlpath = get_setting('module', 'resumes', 'url')
if not urlpath:
    urlpath = "resumes"

urlpatterns = [
    url(r'^%s/$' % urlpath, views.search, name="resumes"),
    url(r'^%s/search/$' % urlpath, views.search_redirect, name="resume.search"),
    url(r'^%s/print-view/(?P<slug>[\w\-\/]+)/$' % urlpath, views.print_view, name="resume.print_view"),
    url(r'^%s/add/$' % urlpath, views.add, name="resume.add"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="resume.edit"),
    url(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, views.edit_meta, name="resume.edit.meta"),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="resume.delete"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='resume.feed'),
    url(r'^%s/pending/$' % urlpath, views.pending, name="resume.pending"),
    url(r'^%s/approve/(?P<id>\d+)/$' % urlpath, views.approve, name="resume.approve"),
    url(r'^%s/thank-you/$' % urlpath, views.thank_you, name="resume.thank_you"),
    url(r'^%s/export/$' % urlpath, views.export, name="resume.export"),
    url(r'^%s/(?P<slug>[\w\-\/]+)/file/$' % urlpath, views.resume_file, name="resume.resume_file"),
    url(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, views.index, name="resume"),
]
