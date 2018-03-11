from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.search, name="emails"),
    url(r'^search/$', views.search, name="email.search"),
    url(r'^(?P<id>\d+)/$', views.view, name="email.view"),
    url(r'^viewbody/(?P<id>\d+)/$', views.view,
        {'template_name': 'emails/viewbody.html'},
        name="email.viewbody"),
    url(r'^add/$', views.add, name="email.add"),
    url(r'^edit/(?P<id>\d+)/$', views.edit, name="email.edit"),
    url(r'^delete/(?P<id>\d+)/$', views.delete, name="email.delete"),
    url(r'^amazon_ses/$', views.amazon_ses_index,
        name="email.amazon_ses_index"),
    url(r'^amazon_ses/verify_email/$', views.amazon_ses_verify_email,
        name="email.amazon_ses_verify_email"),
    url(r'^amazon_ses/list_verified_emails/$', views.amazon_ses_list_verified_emails,
        name="email.amazon_ses_list_verified_emails"),
    url(r'^amazon_ses/send_quota/$', views.amazon_ses_send_quota,
        name="email.amazon_ses_send_quota"),
]
