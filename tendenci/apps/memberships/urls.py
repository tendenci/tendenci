from django.conf.urls import url, include
from tendenci.apps.site_settings.utils import get_setting
from . import views
from tendenci.apps.profiles.views import search as profiles_search

urlpath = get_setting('module', 'memberships', 'url')
if not urlpath:
    urlpath = "memberships"

urlpatterns = [

    # memberships
    url(r"^%s/$" % urlpath, views.membership_index, name="membership.index"),
#     url(r"^%s/search/$" % urlpath, views.membership_search, name="membership.search"),
    url(r"^%s/(?P<id>\d+)/$" % urlpath, views.membership_details, name="membership.details"),
    url(r"^%s/delete/(?P<id>\d+)/$" % urlpath, views.delete, name="membership.delete"),
    url(r"^%s/expire/(?P<id>\d+)/$" % urlpath, views.expire, name="membership.expire"),
    url(r"^%s/add_directory/(?P<id>\d+)/$" % urlpath, views.membership_add_directory, name="membership.add_directory"),
    url(r'^%s/message/pending_members/$' % urlpath, views.message_pending_members, name='membership.message_pending'),
    url(r'^%s/message/pending_members/(?P<email_id>\d+)/$' % urlpath, views.message_pending_members, name='membership.message_pending'),

    # import to membership default
    url(r"^%s/import_default/$" % urlpath, views.membership_default_import_upload,
        name="memberships.default_import"),
    url(r"^%s/import_default/download/$" % urlpath, views.download_default_template,
        name="memberships.download_default_template"),
    url(r"^%s/import_default/preview/(?P<mimport_id>\d+)/$" % urlpath,
        views.membership_default_import_preview,
        name="memberships.default_import_preview"),
    url(r"^%s/import_default/process/(?P<mimport_id>\d+)/$" % urlpath,
        views.membership_default_import_process,
        name="memberships.default_import_process"),
    url(r"^%s/import_default/status/(?P<mimport_id>\d+)/$" % urlpath,
        views.membership_default_import_status,
        name="memberships.default_import_status"),
    url(r"^%s/import_default/get_status/(?P<mimport_id>\d+)/$" % urlpath,
        views.membership_default_import_get_status,
        name="memberships.default_import_get_status"),
    url(r"^%s/import_default/check_encode_status/(?P<mimport_id>\d+)/$" % urlpath,
        views.membership_default_import_check_preprocess_status,
        name="memberships.default_import_check_preprocess_status"),
    url(r"^%s/import_default/download_recap/(?P<mimport_id>\d+)/$" % urlpath,
        views.membership_default_import_download_recap,
        name="memberships.default_import_download_recap"),

    # export membership default
    url(r"^%s/export/$" % urlpath,
        views.membership_default_export,
        name="memberships.default_export"),
    url(r"^%s/export/status/(?P<identifier>\d+)/$" % urlpath,
        views.membership_default_export_status,
        name="memberships.default_export_status"),
    url(r"^%s/export/check_status/(?P<identifier>\d+)/$" % urlpath,
        views.membership_default_export_check_status,
        name="memberships.default_export_check_status"),
    url(r"^%s/export/download/(?P<identifier>\d+)/$" % urlpath,
        views.membership_default_export_download,
        name="memberships.default_export_download"),

    url(r"^%s/get_app_fields/$" % urlpath,
        views.get_app_fields_json,
        name="memberships.get_app_fields"),

    url(r"^%s/get_taken_fields/$" % urlpath,
        views.get_taken_fields,
        name="memberships.get_taken_fields"),

    # corp individual add pre
    url(r"^%s/applications/corp-pre-add/(?P<cm_id>\d+)?/?$" % urlpath,
        views.membership_default_corp_pre_add,
        name="membership_default.corp_pre_add"),
    url(r"^%s/emailtoverify/conf/$" % urlpath,
        views.email_to_verify_conf,
        name="membership.email__to_verify_conf"),
    url(r"^%s/verifyemail/(?P<id>\d+)/(?P<guid>[\d\w-]+)/$" % urlpath,
        views.verify_email,
        name="membership.verify_email"),

    url(r"^%s/applications/add/(?P<cm_id>\d+)/$" % urlpath,
        views.membership_default_add, {'join_under_corporate': True},
        name="membership_default.add_under_corp"),
    url(r"^%s/applications/add/(?P<cm_id>\d+)/(?P<imv_id>\d+)/(?P<imv_guid>[\d\w-]+)/$" % urlpath,
        views.membership_default_add, {'join_under_corporate': True},
        name="membership_default.add_via_corp_domain"),
    url(r"^%s/applications/add/(?P<cm_id>\d+)/(?P<secret_hash>[\d\w]+)$" % urlpath,
        views.membership_default_add, {'join_under_corporate': True},
        name="membership.add_via_corp_secret_code"),

    url(r"^%s/applications/renew/(?P<cm_id>\d+)/(?P<membership_id>\d+)/$" % urlpath,
        views.membership_default_add, {'join_under_corporate': True},
        name="membership_default.renew_under_corp"),

    # membership default application preview
    url(r"^%s/applications/(?P<slug>[\w\-]+)/preview/$" % urlpath,
        views.membership_default_preview,
        name="membership_default.preview"),

    # legacy link for default add
    url(r"^%s/applications/add/$" % urlpath,
        views.membership_default_add_legacy,
        name="membership_default.add"),

    # membership default add
    url(r"^%s/applications/(?P<slug>[\w\-]+)/$" % urlpath,
        views.membership_default_add,
        name="membership_default.add"),

    # membership default renew
    url(r"^%s/applications/(?P<slug>[\w\-]+)/(?P<membership_id>\d+)/$" % urlpath,
        views.membership_default_add,
        name="membership_default.renew"),

    # membership default edit
    url(r"^%s/applications/(?P<id>\d+)/edit/$" % urlpath,
        views.membership_default_edit,
        name="membership_default.edit"),

    # auto-renew set up
    url(r"^%s/auto_renew_setup/(?P<user_id>\d+)/$" % urlpath,
        views.memberships_auto_renew_setup,
        name="memberships.auto_renew_setup"),

    url(r"^%s/applications/$" % urlpath, views.membership_applications, name="membership-applications"),
    url(r"^%s/referer-url/$" % urlpath, views.referer_url, name="membership-referer-url"),

    # reports
    url(r'^%s/reports/$' % urlpath, views.report_list, name='reports-memberships'),
    url(r'^%s/reports/overview/$' % urlpath, views.memberships_overview, name='reports-memberships_overview'),
    url(r'^%s/reports/join_summary$' % urlpath, views.membership_join_report, name='reports-memberships-joins'),
    # See the comments in reports.py
    #url(r'^%s/reports/pdf/$' % urlpath, views.membership_join_report_pdf, name='reports-memberships-joins-pdf'),
    url(r'^%s/reports/active_members/$' % urlpath, views.report_active_members, name='reports-active-members'),
    url(r'^%s/reports/expired_members/$' % urlpath, views.report_expired_members, name='reports-expired-members'),
    url(r'^%s/reports/members_summary/$' % urlpath, views.report_members_summary, name='reports-members-summary'),
    url(r'^%s/reports/members_over_time/$' % urlpath, views.report_members_over_time, name='reports-members-over-time'),
    url(r'^%s/reports/members_stats/$' % urlpath, views.report_members_stats, name='reports-members-stats'),
    url(r'^%s/reports/member_roster/$' % urlpath, views.report_member_roster, name='reports-member-roster'),
    url(r'^%s/reports/member_quick_list/$' % urlpath, views.report_member_quick_list, name='reports-members-quick-list'),
    url(r'^%s/reports/members_by_company/$' % urlpath, views.report_members_by_company, name='reports-members-by-company'),
    url(r'^%s/reports/members_in_renewal_period/$' % urlpath, views.report_renewal_period_members, name='reports-renewal-period-members'),
    url(r'^%s/reports/members_in_grace_period/$' % urlpath, views.report_grace_period_members, name='reports-grace-period-members'),
    url(r'^%s/reports/renewed_members/$' % urlpath, views.report_renewed_members, name='reports-renewed-members'),
    url(r'^%s/reports/active_members_ytd/$' % urlpath, views.report_active_members_ytd, name='reports-active-members-ytd'),
    url(r'^%s/reports/members_ytd_type/$' % urlpath, views.report_members_ytd_type, name='reports-members-ytd-type'),
    url(r'^%s/reports/members_donated/$' % urlpath, views.report_members_donated, name='reports-members-donated'),

    url(r"^%s/entries/search/$" % urlpath, views.application_entries_search, name="membership.application_entries_search"),

    # notice
    url(r'^%s/notices/' % urlpath, include('tendenci.apps.memberships.notices.urls')),
    url(r"^%s/notices/(?P<id>\d+)/email_content/$" % urlpath, views.notice_email_content, name="membership.notice_email_content"),


    # application
    url(r"^%s/default-confirmation/(?P<hash>[\w]+)/$" % urlpath, views.application_confirmation_default, name="membership.application_confirmation_default"),
    url(r"^%s/default-application/(?P<cmb_id>\d+)?/?$" % urlpath, views.application_detail_default, name="membership.application_detail_default"),

]

urlpatterns += [url(r'^%s/search/$' % urlpath, profiles_search, {'memberships_search': True }, name="membership.search",),]
