from django.conf.urls import patterns, url

urlpatterns = patterns('tendenci.apps.contacts',
    url(r'^contacts/$', 'views.search', name="contacts"),
    url(r'^contacts/(?P<id>\d+)/$', 'views.details', name="contact"),
    url(r'^contacts/search/$', 'views.search_redirect', name="contact.search"),
    url(r'^contacts/print-view/(?P<id>\d+)/$', 'views.print_view', name="contact.print_view"),
    url(r'^contacts/delete/(?P<id>\d+)/$', 'views.delete', name="contact.delete"),

    # site contact form
    url(r'^contact/$', 'views.index', name="form"),
    url(r'^contact/confirmation$', 'views.confirmation', name="form.confirmation"),

)