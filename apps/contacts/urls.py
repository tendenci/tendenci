from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('contacts',                  
    url(r'^$', 'views.search', name="contacts"),
    url(r'^(?P<id>\d+)/$', 'views.details', name="contact"),
    url(r'^search/$', 'views.search_redirect', name="contact.search"),
    url(r'^print-view/(?P<id>\d+)/$', 'views.print_view', name="contact.print_view"),
    url(r'^delete/(?P<id>\d+)/$', 'views.delete', name="contact.delete"),
)