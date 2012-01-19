from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',                  
    url(r'^$', 'locations.views.index', name="locations"),
    url(r'^(?P<id>\d+)/$', 'locations.views.index', name="location"),
    url(r'^search/$', 'locations.views.search', name="location.search"),
    url(r'^nearest/$', 'locations.views.nearest', name="location.nearest"),
    url(r'^print-view/(?P<id>\d+)/$', 'locations.views.print_view', name="location.print_view"),
    url(r'^add/$', 'locations.views.add', name="location.add"),
    url(r'^edit/(?P<id>\d+)/$', 'locations.views.edit', name="location.edit"),
    url(r'^delete/(?P<id>\d+)/$', 'locations.views.delete', name="location.delete"),
)