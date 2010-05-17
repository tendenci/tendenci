from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',                  
    url(r'^$', 'pages.views.index', name="pages"),
    url(r'^(?P<id>\d+)/$', 'pages.views.index', name="page"),
    url(r'^search/$', 'pages.views.search', name="page.search"),
    url(r'^print-view/(?P<id>\d+)/$', 'pages.views.print_view', name="page.print_view"),
    url(r'^edit/(?P<id>\d+)/$', 'pages.views.edit', name="page.edit"),
    url(r'^delete/(?P<id>\d+)/$', 'pages.views.delete', name="page.delete"),
)