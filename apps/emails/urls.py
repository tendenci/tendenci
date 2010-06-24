from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('emails.views',                  
    url(r'^$', 'search', name="emails"),
    url(r'^(?P<id>\d+)/$', 'view', name="email.view"),
    url(r'^viewbody/(?P<id>\d+)/$', 'view', 
        {'template_name': 'emails/viewbody.html'}, 
        name="email.viewbody"),
    url(r'^search/$', 'search', name="email.search"),
    url(r'^add/$', 'add', name="email.add"),
    url(r'^edit/(?P<id>\d+)/$', 'edit', name="email.edit"),
    url(r'^delete/(?P<id>\d+)/$', 'delete', name="email.delete"),
)