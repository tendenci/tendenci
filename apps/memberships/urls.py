from django.conf.urls.defaults import *

urlpatterns = patterns("memberships.views",

    # memberships
    url(r"^$", "membership_index", name="membership.index"),
    url(r"^search/$", "membership_search", name="membership.search"),
    url(r"^(?P<id>\d+)/$", "membership_details", name="membership.details"),
    url(r"^(?P<id>\d+)/delete/$", "membership_delete", name="membership.delete"),
    url(r"^(?P<id>\d+)/edit/$", "membership_edit", name="membership.edit"),

    # notices
    (r'^notices/', include('memberships.notices.urls')),
    
    # import
    url(r"^import/$", "membership_import_upload", name="membership_import"),
    url(r"^import/upload-file$", "membership_import_upload", name="membership_import_upload_file"),
    url(r"^import/preview/(?P<id>\d+)/$", "membership_import_preview", name="membership_import_preview"),
    url(r"^import/confirm/(?P<id>\d+)/$", "membership_import_confirm", name="membership_import_confirm"),
    url(r"^import/status/(?P<task_id>[-\w]+)/$", "membership_import_status", name='membership_import_status'),
    
    # export
    url(r"^export/$", "membership_export", name="membership_export"),

    # reports
    url(r'^reports/$', 'membership_join_report', name='reports-memberships-joins'),
    url(r'^reports/pdf/$', 'membership_join_report_pdf', name='reports-memberships-joins-pdf'),
    url(r'^reports/active_members/$', 'report_active_members', name='reports-active-members'),
    url(r'^reports/expired_members/$', 'report_expired_members', name='reports-expired-members'),
    url(r'^reports/members_summary/$', 'report_members_summary', name='reports-members-summary'),
    url(r'^reports/members_over_time/$', 'report_members_over_time', name='reports-members-over-time'),
    url(r'^reports/members_stats/$', 'report_members_stats', name='reports-members-stats'),

    # entries
    url(r"^entries/$", "application_entries", name="membership.application_entries"),
    url(r"^entries/(?P<id>\d+)/$", "application_entries", name="membership.application_entries"),
    url(r"^entries/print/(?P<id>\d+)/$", "application_entries_print", name="membership.application_entries_print"),
    url(r"^entries/edit/(?P<id>\d+)/$", "entry_edit", name="membership.entry_edit"),
    url(r"^entries/delete/(?P<id>\d+)/$", "entry_delete", name="membership.entry_delete"),
    url(r"^entries/search/$", "application_entries_search", name="membership.application_entries_search"),

    # notice
    url(r"^notices/(?P<id>\d+)/email_content/$", "notice_email_content", name="membership.notice_email_content"),
    
    url(r"^emailtoverify/conf/$", "email_to_verify_conf", name="membership.email__to_verify_conf"),
    url(r"^verifyemail/(?P<id>\d+)/(?P<guid>[\d\w-]+)/$", "verify_email", name="membership.verify_email"),

    # application
    url(r"^confirmation/(?P<hash>[\w]+)/$", "application_confirmation", name="membership.application_confirmation"),

    url(r"^(?P<slug>[\w\-]+)/template/$", "download_template", name="membership.download_template"),
    url(r"^(?P<slug>[\w\-]+)/(?P<cmb_id>\d+)?/?$", "application_details", name="membership.application_details"),
    url(r"^(?P<slug>[\w\-]+)/(?P<cmb_id>\d+)/(?P<imv_id>\d+)/(?P<imv_guid>[\d\w-]+)/$", "application_details", name="membership.application_details_via_corp_domain"),
    url(r"^(?P<slug>[\w\-]+)/(?P<cmb_id>\d+)/(?P<secret_hash>[\d\w]+)$", "application_details", name="membership.application_details_via_corp_secret_code"),
    url(r"^(?P<slug>[\w\-]+)/corp-pre/(?P<cmb_id>\d+)?/?$", "application_details_corp_pre", name="membership.application_details_corp_pre"),
)
