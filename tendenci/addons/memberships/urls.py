from django.conf.urls.defaults import *

urlpatterns = patterns("tendenci.addons.memberships.views",

    # memberships
    url(r"^$", "membership_index", name="membership.index"),
    url(r"^search/$", "membership_search", name="membership.search"),
    url(r"^(?P<id>\d+)/$", "membership_details", name="membership.details"),
    url(r"^(?P<id>\d+)/delete/$", "membership_delete", name="membership.delete"),
    url(r"^(?P<id>\d+)/edit/$", "membership_edit", name="membership.edit"),
    url(r"^entries-export/$", "membership_export"),

    # import
    url(r"^import/$", "membership_import_upload", name="membership_import"),
    url(r"^import/upload-file$", "membership_import_upload", name="membership_import_upload_file"),
    url(r"^import/preview/(?P<id>\d+)/$", "membership_import_preview", name="membership_import_preview"),
    url(r"^import/confirm/(?P<id>\d+)/$", "membership_import_confirm", name="membership_import_confirm"),
    url(r"^import/status/(?P<task_id>[-\w]+)/$", "membership_import_status", name='membership_import_status'),

    # import to membership default
    url(r"^import_default/$", "membership_default_import_upload",
        name="memberships.default_import"),
    url(r"^import_default/download/$", "download_default_template",
        name="memberships.download_default_template"),
    url(r"^import_default/preview/(?P<mimport_id>\d+)/$",
        "membership_default_import_preview",
        name="memberships.default_import_preview"),
    url(r"^import_default/process/(?P<mimport_id>\d+)/$",
        "membership_default_import_process",
        name="memberships.default_import_process"),
    url(r"^import_default/status/(?P<mimport_id>\d+)/$",
        "membership_default_import_status",
        name="memberships.default_import_status"),
    url(r"^import_default/get_status/(?P<mimport_id>\d+)/$",
        "membership_default_import_get_status",
        name="memberships.default_import_get_status"),
    url(r"^import_default/check_encode_status/(?P<mimport_id>\d+)/$",
        "membership_default_import_check_preprocess_status",
        name="memberships.default_import_check_preprocess_status"),

    # export membership default
    url(r"^export/$",
        "membership_default_export",
        name="memberships.default_export"),
    url(r"^export/status/(?P<identifier>\d+)/$",
        "membership_default_export_status",
        name="memberships.default_export_status"),
    url(r"^export/check_status/(?P<identifier>\d+)/$",
        "membership_default_export_check_status",
        name="memberships.default_export_check_status"),
    url(r"^export/download/(?P<identifier>\d+)/$",
        "membership_default_export_download",
        name="memberships.default_export_download"),

    url(r"^get_app_fields/$",
        "get_app_fields_json",
        name="memberships.get_app_fields"),

    # membership default application preview
    url(r"^applications/(?P<app_id>\d+)/preview/$",
        "membership_default_preview",
        name="membership_default.preview"),
    # corp individual add pre
    url(r"^applications/corp-pre-add/(?P<cm_id>\d+)?/?$",
        "membership_default_corp_pre_add",
        name="membership_default.corp_pre_add"),
    url(r"^emailtoverify/conf/$",
        "email_to_verify_conf",
        name="membership.email__to_verify_conf"),
    url(r"^verifyemail/(?P<id>\d+)/(?P<guid>[\d\w-]+)/$",
        "verify_email",
        name="membership.verify_email"),
    # membership default add
    url(r"^applications/add/$",
        "membership_default_add",
        name="membership_default.add"),
    url(r"^applications/add/(?P<cm_id>\d+)/$",
        "membership_default_add", {'join_under_corporate': True},
        name="membership_default.add_under_corp"),
    url(r"^applications/add/(?P<cm_id>\d+)/(?P<imv_id>\d+)/(?P<imv_guid>[\d\w-]+)/$",
        "membership_default_add", {'join_under_corporate': True},
        name="membership_default.add_via_corp_domain"),
    url(r"^applications/add/(?P<cm_id>\d+)/(?P<secret_hash>[\d\w]+)$",
        "membership_default_add", {'join_under_corporate': True},
        name="membership.add_via_corp_secret_code"),

    # reports
    url(r'^reports/$', 'report_list', name='reports-memberships'),
    url(r'^reports/join_summary$', 'membership_join_report', name='reports-memberships-joins'),
    url(r'^reports/pdf/$', 'membership_join_report_pdf', name='reports-memberships-joins-pdf'),
    url(r'^reports/active_members/$', 'report_active_members', name='reports-active-members'),
    url(r'^reports/expired_members/$', 'report_expired_members', name='reports-expired-members'),
    url(r'^reports/members_summary/$', 'report_members_summary', name='reports-members-summary'),
    url(r'^reports/members_over_time/$', 'report_members_over_time', name='reports-members-over-time'),
    url(r'^reports/members_stats/$', 'report_members_stats', name='reports-members-stats'),
    url(r'^reports/member_roster/$', 'report_member_roster', name='reports-member-roster'),
    url(r'^reports/member_quick_list/$', 'report_member_quick_list', name='reports-members-quick-list'),
    url(r'^reports/members_by_company/$', 'report_members_by_company', name='reports-members-by-company'),
    url(r'^reports/members_in_renewal_period/$', 'report_renewal_period_members', name='reports-renewal-period-members'),
    url(r'^reports/members_in_grace_period/$', 'report_grace_period_members', name='reports-grace-period-members'),
    url(r'^reports/renewed_members/$', 'report_renewed_members', name='reports-renewed-members'),
    url(r'^reports/active_members_ytd/$', 'report_active_members_ytd', name='reports-active-members-ytd'),
    url(r'^reports/members_ytd_type/$', 'report_members_ytd_type', name='reports-members-ytd-type'),

    # entries
    url(r"^entries/$", "application_entries", name="membership.application_entries"),
    url(r"^entries/(?P<id>\d+)/$", "application_entries", name="membership.application_entries"),
    url(r"^entries/print/(?P<id>\d+)/$", "application_entries_print", name="membership.application_entries_print"),
    url(r"^entries/edit/(?P<id>\d+)/$", "entry_edit", name="membership.entry_edit"),
    url(r"^entries/delete/(?P<id>\d+)/$", "entry_delete", name="membership.entry_delete"),
    url(r"^entries/search/$", "application_entries_search", name="membership.application_entries_search"),

    # notice
    (r'^notices/', include('tendenci.addons.memberships.notices.urls')),
    url(r"^notices/(?P<id>\d+)/email_content/$", "notice_email_content", name="membership.notice_email_content"),


    # application
    url(r"^confirmation/(?P<hash>[\w]+)/$", "application_confirmation", name="membership.application_confirmation"),
    url(r"^default-confirmation/(?P<hash>[\w]+)/$", "application_confirmation_default", name="membership.application_confirmation_default"),
    url(r"^(?P<slug>[\w\-]+)/template/$", "download_template", name="membership.download_template"),
    url(r"^default-application/(?P<cmb_id>\d+)?/?$", "application_detail_default", name="membership.application_detail_default"),
    url(r"^(?P<slug>[\w\-]+)/(?P<cmb_id>\d+)?/?$", "application_details", name="membership.application_details"),
    url(r"^(?P<slug>[\w\-]+)/(?P<cmb_id>\d+)/(?P<imv_id>\d+)/(?P<imv_guid>[\d\w-]+)/$", "application_details", name="membership.application_details_via_corp_domain"),
    url(r"^(?P<slug>[\w\-]+)/(?P<cmb_id>\d+)/(?P<secret_hash>[\d\w]+)$", "application_details", name="membership.application_details_via_corp_secret_code"),
    url(r"^(?P<slug>[\w\-]+)/corp-pre/(?P<cmb_id>\d+)?/?$", "application_details_corp_pre", name="membership.application_details_corp_pre"),
)
