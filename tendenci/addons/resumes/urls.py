from django.conf.urls.defaults import patterns, url
from tendenci.addons.resumes.feeds import LatestEntriesFeed
from tendenci.core.site_settings.utils import get_setting
from tendenci.addons.resumes.signals import init_signals

init_signals()

urlpath = get_setting('module', 'resumes', 'url')
if not urlpath:
    urlpath = "resumes"

urlpatterns = patterns('tendenci.addons.resumes.views',
    url(r'^%s/$' % urlpath, 'search', name="resumes"),
    url(r'^%s/search/$' % urlpath, 'search_redirect', name="resume.search"),
    url(r'^%s/print-view/(?P<slug>[\w\-\/]+)/$' % urlpath, 'print_view', name="resume.print_view"),
    url(r'^%s/add/$' % urlpath, 'add', name="resume.add"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, 'edit', name="resume.edit"),
    url(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, 'edit_meta', name="resume.edit.meta"),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, 'delete', name="resume.delete"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='resume.feed'),
    url(r'^%s/pending/$' % urlpath, 'pending', name="resume.pending"),
    url(r'^%s/approve/(?P<id>\d+)/$' % urlpath, 'approve', name="resume.approve"),
    url(r'^%s/thank-you/$' % urlpath, 'thank_you', name="resume.thank_you"),
    url(r'^%s/export/$' % urlpath, 'export', name="resume.export"),
    url(r'^%s/(?P<slug>[\w\-\/]+)/file/$' % urlpath, 'resume_file', name="resume.resume_file"),
    url(r'^%s/(?P<slug>[\w\-\/]+)/$' % urlpath, 'index', name="resume"),
)
