from django.conf.urls import patterns, url, include


urlpatterns = patterns('tendenci.apps.emails.views',
    url(r'^$', 'search', name="emails"),
    url(r'^search/$', 'search', name="email.search"),
    url(r'^(?P<id>\d+)/$', 'view', name="email.view"),
    url(r'^viewbody/(?P<id>\d+)/$', 'view',
        {'template_name': 'emails/viewbody.html'},
        name="email.viewbody"),
    url(r'^add/$', 'add', name="email.add"),
    url(r'^edit/(?P<id>\d+)/$', 'edit', name="email.edit"),
    url(r'^delete/(?P<id>\d+)/$', 'delete', name="email.delete"),
    url(r'^amazon_ses/$', 'amazon_ses_index',
        name="email.amazon_ses_index"),
    url(r'^amazon_ses/verify_email/$', 'amazon_ses_verify_email',
        name="email.amazon_ses_verify_email"),
    url(r'^amazon_ses/list_verified_emails/$', 'amazon_ses_list_verified_emails',
        name="email.amazon_ses_list_verified_emails"),
    url(r'^amazon_ses/send_quota/$', 'amazon_ses_send_quota',
        name="email.amazon_ses_send_quota"),
    (r'^blocks/', include('tendenci.apps.email_blocks.urls')),
)
