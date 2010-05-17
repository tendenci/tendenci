from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',                  
    url(r'^$', 'releases.views.index', name="releases"),
    url(r'^(?P<id>\d+)/$', 'releases.views.index', name="release"),
    url(r'^search/$', 'releases.views.search', name="release.search"),
    url(r'^print-view/(?P<id>\d+)/$', 'releases.views.print_view', name="release.print_view"),
    url(r'^edit/(?P<id>\d+)/$', 'releases.views.edit', name="release.edit"),
    url(r'^delete/(?P<id>\d+)/$', 'releases.views.delete', name="release.delete"),
)