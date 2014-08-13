from django.conf.urls.defaults import patterns, url, include
from tendenci.core.site_settings.utils import get_setting

urlpath = get_setting('module', 'memberships', 'url')
if not urlpath:
    urlpath = "memberships"

urlpatterns = patterns(
    "tendenci.addons.memberships.views",

    # memberships
    url(r"^%s/$" % urlpath, "membership_index", name="membership.index"),
    url(r"^%s/search/$" % urlpath, "membership_search", name="membership.search"),
    url(r"^%s/(?P<id>\d+)/$" % urlpath, "membership_details", name="membership.details"),

    # import to membership default
    url(r"^%s/import_default/$" % urlpath, "membership_default_import_upload",
        name="memberships.default_import"),
    url(r"^%s/import_default/download/$" % urlpath, "download_default_template",
        name="memberships.download_default_template"),
    url(r"^%s/import_default/preview/(?P<mimport_id>\d+)/$" % urlpath,
        "membership_default_import_preview",
        name="memberships.default_import_preview"),
    url(r"^%s/import_default/process/(?P<mimport_id>\d+)/$" % urlpath,
        "membership_default_import_process",
        name="memberships.default_import_process"),
    url(r"^%s/import_default/status/(?P<mimport_id>\d+)/$" % urlpath,
        "membership_default_import_status",
        name="memberships.default_import_status"),
    url(r"^%s/import_default/get_status/(?P<mimport_id>\d+)/$" % urlpath,
        "membership_default_import_get_status",
        name="memberships.default_import_get_status"),
    url(r"^%s/import_default/check_encode_status/(?P<mimport_id>\d+)/$" % urlpath,
        "membership_default_import_check_preprocess_status",
        name="memberships.default_import_check_preprocess_status"),
    url(r"^%s/import_default/download_recap/(?P<mimport_id>\d+)/$" % urlpath,
        "membership_default_import_download_recap",
        name="memberships.default_import_download_recap"),

    # export membership default
    url(r"^%s/export/$" % urlpath,
        "membership_default_export",
        name="memberships.default_export"),
    url(r"^%s/export/status/(?P<identifier>\d+)/$" % urlpath,
        "membership_default_export_status",
        name="memberships.default_export_status"),
    url(r"^%s/export/check_status/(?P<identifier>\d+)/$" % urlpath,
        "membership_default_export_check_status",
        name="memberships.default_export_check_status"),
    url(r"^%s/export/download/(?P<identifier>\d+)/$" % urlpath,
        "membership_default_export_download",
        name="memberships.default_export_download"),

    url(r"^%s/get_app_fields/$" % urlpath,
        "get_app_fields_json",
        name="memberships.get_app_fields"),

    url(r"^%s/get_taken_fields/$" % urlpath,
        "get_taken_fields",
        name="memberships.get_taken_fields"),

    # corp individual add pre
    url(r"^%s/applications/corp-pre-add/(?P<cm_id>\d+)?/?$" % urlpath,
        "membership_default_corp_pre_add",
        name="membership_default.corp_pre_add"),
    url(r"^%s/emailtoverify/conf/$" % urlpath,
        "email_to_verify_conf",
        name="membership.email__to_verify_conf"),
    url(r"^%s/verifyemail/(?P<id>\d+)/(?P<guid>[\d\w-]+)/$" % urlpath,
        "verify_email",
        name="membership.verify_email"),

    url(r"^%s/applications/add/(?P<cm_id>\d+)/$" % urlpath,
        "membership_default_add", {'join_under_corporate': True},
        name="membership_default.add_under_corp"),
    url(r"^%s/applications/add/(?P<cm_id>\d+)/(?P<imv_id>\d+)/(?P<imv_guid>[\d\w-]+)/$" % urlpath,
        "membership_default_add", {'join_under_corporate': True},
        name="membership_default.add_via_corp_domain"),
    url(r"^%s/applications/add/(?P<cm_id>\d+)/(?P<secret_hash>[\d\w]+)$" % urlpath,
        "membership_default_add", {'join_under_corporate': True},
        name="membership.add_via_corp_secret_code"),

    url(r"^%s/applications/renew/(?P<cm_id>\d+)/(?P<membership_id>\d+)/$" % urlpath,
        "membership_default_add", {'join_under_corporate': True},
        name="membership_default.renew_under_corp"),

    # membership default application preview
    url(r"^%s/applications/(?P<slug>[\w\-]+)/preview/$" % urlpath,
        "membership_default_preview",
        name="membership_default.preview"),

    # legacy link for default add
    url(r"^%s/applications/add/$" % urlpath,
        "membership_default_add_legacy",
        name="membership_default.add"),

    # membership default add
    url(r"^%s/applications/(?P<slug>[\w\-]+)/$" % urlpath,
        "membership_default_add",
        name="membership_default.add"),
                       
    # membership default renew
    url(r"^%s/applications/(?P<slug>[\w\-]+)/(?P<membership_id>\d+)/$" % urlpath,
        "membership_default_add",
        name="membership_default.renew"),

    # membership default edit
    url(r"^%s/applications/(?P<id>\d+)/edit/$" % urlpath,
        "membership_default_edit",
        name="membership_default.edit"),

    url(r"^%s/applications/$" % urlpath, "membership_applications", name="membership-applications"),
    url(r"^%s/referer-url/$" % urlpath, "referer_url", name="membership-referer-url"),

    # reports
    url(r'^%s/reports/$' % urlpath, 'report_list', name='reports-memberships'),
    url(r'^%s/reports/join_summary$' % urlpath, 'membership_join_report', name='reports-memberships-joins'),
    url(r'^%s/reports/pdf/$' % urlpath, 'membership_join_report_pdf', name='reports-memberships-joins-pdf'),
    url(r'^%s/reports/active_members/$' % urlpath, 'report_active_members', name='reports-active-members'),
    url(r'^%s/reports/expired_members/$' % urlpath, 'report_expired_members', name='reports-expired-members'),
    url(r'^%s/reports/members_summary/$' % urlpath, 'report_members_summary', name='reports-members-summary'),
    url(r'^%s/reports/members_over_time/$' % urlpath, 'report_members_over_time', name='reports-members-over-time'),
    url(r'^%s/reports/members_stats/$' % urlpath, 'report_members_stats', name='reports-members-stats'),
    url(r'^%s/reports/member_roster/$' % urlpath, 'report_member_roster', name='reports-member-roster'),
    url(r'^%s/reports/member_quick_list/$' % urlpath, 'report_member_quick_list', name='reports-members-quick-list'),
    url(r'^%s/reports/members_by_company/$' % urlpath, 'report_members_by_company', name='reports-members-by-company'),
    url(r'^%s/reports/members_in_renewal_period/$' % urlpath, 'report_renewal_period_members', name='reports-renewal-period-members'),
    url(r'^%s/reports/members_in_grace_period/$' % urlpath, 'report_grace_period_members', name='reports-grace-period-members'),
    url(r'^%s/reports/renewed_members/$' % urlpath, 'report_renewed_members', name='reports-renewed-members'),
    url(r'^%s/reports/active_members_ytd/$' % urlpath, 'report_active_members_ytd', name='reports-active-members-ytd'),
    url(r'^%s/reports/members_ytd_type/$' % urlpath, 'report_members_ytd_type', name='reports-members-ytd-type'),

     url(r"^%s/entries/search/$" % urlpath, "application_entries_search", name="membership.application_entries_search"),

    # notice
    (r'^%s/notices/' % urlpath, include('tendenci.addons.memberships.notices.urls')),
    url(r"^%s/notices/(?P<id>\d+)/email_content/$" % urlpath, "notice_email_content", name="membership.notice_email_content"),


#     # application
     url(r"^%s/default-confirmation/(?P<hash>[\w]+)/$" % urlpath, "application_confirmation_default", name="membership.application_confirmation_default"),
     url(r"^%s/default-application/(?P<cmb_id>\d+)?/?$" % urlpath, "application_detail_default", name="membership.application_detail_default"),

)
