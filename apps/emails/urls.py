from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('',                  
    url(r'^$', 'emails.views.search', name="emails"),
    url(r'^search/$', 'emails.views.search', name="email.search"),
    url(r'^(?P<id>\d+)/$', 'emails.views.view', name="email.view"),
    url(r'^viewbody/(?P<id>\d+)/$', 'emails.views.view', 
        {'template_name': 'emails/viewbody.html'}, 
        name="email.viewbody"),
    url(r'^add/$', 'emails.views.add', name="email.add"),
    url(r'^edit/(?P<id>\d+)/$', 'emails.views.edit', name="email.edit"),
    url(r'^delete/(?P<id>\d+)/$', 'emails.views.delete', name="email.delete"),
    url(r'^amazon_ses/verify_email/$', 'emails.views.amazon_ses_verify_email', 
        name="email.amazon_ses_verify_email"),
    url(r'^amazon_ses/list_verified_emails/$', 'emails.views.amazon_ses_list_verified_emails', 
        name="email.amazon_ses_list_verified_emails"),
    (r'^blocks/', include('email_blocks.urls')),
)