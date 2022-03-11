from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.search, name="emails"),
    re_path(r'^search/$', views.search, name="email.search"),
    re_path(r'^(?P<id>\d+)/$', views.view, name="email.view"),
    re_path(r'^viewbody/(?P<id>\d+)/$', views.view,
        {'template_name': 'emails/viewbody.html'},
        name="email.viewbody"),
    re_path(r'^add/$', views.add, name="email.add"),
    re_path(r'^edit/(?P<id>\d+)/$', views.edit, name="email.edit"),
    re_path(r'^delete/(?P<id>\d+)/$', views.delete, name="email.delete"),
    re_path(r'^amazon_ses/$', views.amazon_ses_index,
        name="email.amazon_ses_index"),
    re_path(r'^amazon_ses/verify_email/$', views.amazon_ses_verify_email,
        name="email.amazon_ses_verify_email"),
    re_path(r'^amazon_ses/list_verified_emails/$', views.amazon_ses_list_verified_emails,
        name="email.amazon_ses_list_verified_emails"),
    re_path(r'^amazon_ses/send_quota/$', views.amazon_ses_send_quota,
        name="email.amazon_ses_send_quota"),
]
