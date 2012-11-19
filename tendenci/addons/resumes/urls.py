from django.conf.urls.defaults import patterns, url
from tendenci.addons.resumes.feeds import LatestEntriesFeed

urlpatterns = patterns('tendenci.addons.resumes.views',
    url(r'^$', 'search', name="resumes"),
    url(r'^search/$', 'search_redirect', name="resume.search"),
    url(r'^print-view/(?P<slug>[\w\-\/]+)/$', 'print_view', name="resume.print_view"),
    url(r'^add/$', 'add', name="resume.add"),
    url(r'^edit/(?P<id>\d+)/$', 'edit', name="resume.edit"),
    url(r'^edit/meta/(?P<id>\d+)/$', 'edit_meta', name="resume.edit.meta"),
    url(r'^delete/(?P<id>\d+)/$', 'delete', name="resume.delete"),
    url(r'^feed/$', LatestEntriesFeed(), name='resume.feed'),
    url(r'^pending/$', 'pending', name="resume.pending"),
    url(r'^approve/(?P<id>\d+)/$', 'approve', name="resume.approve"),
    url(r'^thank-you/$', 'thank_you', name="resume.thank_you"),
    url(r'^export/$', 'export', name="resume.export"),
    url(r'^(?P<slug>[\w\-\/]+)/file/$', 'resume_file', name="resume.resume_file"),
    url(r'^(?P<slug>[\w\-\/]+)/$', 'index', name="resume"),
)
