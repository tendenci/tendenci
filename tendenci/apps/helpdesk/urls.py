"""
django-helpdesk - A Django powered ticket tracker for small enterprise.

(c) Copyright 2008 Jutda. All Rights Reserved. See LICENSE for details.

urls.py - Mapping of URL's to our various views. Note we always used NAMED
          views for simplicity in linking later on.
"""

from django.urls import path, re_path
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView

from . import settings as helpdesk_settings
from .views import feeds, staff, public, api, kb
from django.contrib.auth import views as auth_views

from django.views.generic import TemplateView
class DirectTemplateView(TemplateView):
    extra_context = None
    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        if self.extra_context is not None:
            for key, value in self.extra_context.items():
                if callable(value):
                    context[key] = value()
                else:
                    context[key] = value
        return context

urlpatterns = [
    re_path(r'^dashboard/$',
        staff.dashboard,
        name='helpdesk_dashboard'),

    re_path(r'^tickets/$',
        staff.ticket_list,
        name='helpdesk_list'),

    re_path(r'^tickets/update/$',
        staff.mass_update,
        name='helpdesk_mass_update'),

    re_path(r'^tickets/submit/$',
        staff.create_ticket,
        name='helpdesk_submit'),

    re_path(r'^tickets/(?P<ticket_id>[0-9]+)/$',
        staff.view_ticket,
        name='helpdesk_view'),

    re_path(r'^tickets/(?P<ticket_id>[0-9]+)/followup_edit/(?P<followup_id>[0-9]+)/$',
        staff.followup_edit,
        name='helpdesk_followup_edit'),

    re_path(r'^tickets/(?P<ticket_id>[0-9]+)/followup_delete/(?P<followup_id>[0-9]+)/$',
        staff.followup_delete,
        name='helpdesk_followup_delete'),

    re_path(r'^tickets/(?P<ticket_id>[0-9]+)/edit/$',
        staff.edit_ticket,
        name='helpdesk_edit'),

    re_path(r'^tickets/(?P<ticket_id>[0-9]+)/update/$',
        staff.update_ticket,
        name='helpdesk_update'),

    re_path(r'^tickets/(?P<ticket_id>[0-9]+)/delete/$',
        staff.delete_ticket,
        name='helpdesk_delete'),

    re_path(r'^tickets/(?P<ticket_id>[0-9]+)/hold/$',
        staff.hold_ticket,
        name='helpdesk_hold'),

    re_path(r'^tickets/(?P<ticket_id>[0-9]+)/unhold/$',
        staff.unhold_ticket,
        name='helpdesk_unhold'),

    re_path(r'^tickets/(?P<ticket_id>[0-9]+)/cc/$',
        staff.ticket_cc,
        name='helpdesk_ticket_cc'),

    re_path(r'^tickets/(?P<ticket_id>[0-9]+)/cc/add/$',
        staff.ticket_cc_add,
        name='helpdesk_ticket_cc_add'),

    re_path(r'^tickets/(?P<ticket_id>[0-9]+)/cc/delete/(?P<cc_id>[0-9]+)/$',
        staff.ticket_cc_del,
        name='helpdesk_ticket_cc_del'),

    re_path(r'^tickets/(?P<ticket_id>[0-9]+)/dependency/add/$',
        staff.ticket_dependency_add,
        name='helpdesk_ticket_dependency_add'),

    re_path(r'^tickets/(?P<ticket_id>[0-9]+)/dependency/delete/(?P<dependency_id>[0-9]+)/$',
        staff.ticket_dependency_del,
        name='helpdesk_ticket_dependency_del'),

    re_path(r'^tickets/(?P<ticket_id>[0-9]+)/attachment_delete/(?P<attachment_id>[0-9]+)/$',
        staff.attachment_del,
        name='helpdesk_attachment_del'),

    re_path(r'^raw/(?P<type>\w+)/$',
        staff.raw_details,
        name='helpdesk_raw'),

    re_path(r'^rss/$',
        staff.rss_list,
        name='helpdesk_rss_index'),

    re_path(r'^reports/$',
        staff.report_index,
        name='helpdesk_report_index'),

    re_path(r'^reports/(?P<report>\w+)/$',
        staff.run_report,
        name='helpdesk_run_report'),

    re_path(r'^save_query/$',
        staff.save_query,
        name='helpdesk_savequery'),

    re_path(r'^delete_query/(?P<id>[0-9]+)/$',
        staff.delete_saved_query,
        name='helpdesk_delete_query'),

    re_path(r'^settings/$',
        staff.user_settings,
        name='helpdesk_user_settings'),

    re_path(r'^ignore/$',
        staff.email_ignore,
        name='helpdesk_email_ignore'),

    re_path(r'^ignore/add/$',
        staff.email_ignore_add,
        name='helpdesk_email_ignore_add'),

    re_path(r'^ignore/delete/(?P<id>[0-9]+)/$',
        staff.email_ignore_del,
        name='helpdesk_email_ignore_del'),
]

urlpatterns += [
    re_path(r'^$',
        public.homepage,
        name='helpdesk_home'),

    re_path(r'^view/$',
        public.view_ticket,
        name='helpdesk_public_view'),

    re_path(r'^change_language/$',
        public.change_language,
        name='helpdesk_public_change_language'),
]

urlpatterns += [
    re_path(r'^rss/user/(?P<user_name>[^/]+)/$',
        login_required(feeds.OpenTicketsByUser()),
        name='helpdesk_rss_user'),

    re_path(r'^rss/user/(?P<user_name>[^/]+)/(?P<queue_slug>[A-Za-z0-9_-]+)/$',
        login_required(feeds.OpenTicketsByUser()),
        name='helpdesk_rss_user_queue'),

    re_path(r'^rss/queue/(?P<queue_slug>[A-Za-z0-9_-]+)/$',
        login_required(feeds.OpenTicketsByQueue()),
        name='helpdesk_rss_queue'),

    re_path(r'^rss/unassigned/$',
        login_required(feeds.UnassignedTickets()),
        name='helpdesk_rss_unassigned'),

    re_path(r'^rss/recent_activity/$',
        login_required(feeds.RecentFollowUps()),
        name='helpdesk_rss_activity'),
]


urlpatterns += [
    re_path(r'^api/(?P<method>[a-z_-]+)/$',
        api.api,
        name='helpdesk_api'),

#     re_path(r'^login/$',
#         auth_views.login,
#         {'template_name': 'helpdesk/registration/login.html'},
#         name='login'),

    re_path(r'^logout/$',
        LogoutView.as_view(template_name='helpdesk/registration/login.html',
                           next_page='../'),
        name='logout'),
]

if helpdesk_settings.HELPDESK_KB_ENABLED:
    urlpatterns += [
        re_path(r'^kb/$',
            kb.index,
            name='helpdesk_kb_index'),

        re_path(r'^kb/(?P<item>[0-9]+)/$',
            kb.item,
            name='helpdesk_kb_item'),

        re_path(r'^kb/(?P<item>[0-9]+)/vote/$',
            kb.vote,
            name='helpdesk_kb_vote'),

        re_path(r'^kb/(?P<slug>[A-Za-z0-9_-]+)/$',
            kb.category,
            name='helpdesk_kb_category'),
    ]

urlpatterns += [
    re_path(r'^api/$',
        TemplateView.as_view(template_name='helpdesk/help_api.html'),
        name='helpdesk_api_help'),

    re_path(r'^help/context/$',
        TemplateView.as_view(template_name='helpdesk/help_context.html'),
        name='helpdesk_help_context'),

    re_path(r'^system_settings/$',
        DirectTemplateView.as_view(template_name='helpdesk/system_settings.html'),
        name='helpdesk_system_settings'),
]
