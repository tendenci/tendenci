from django.conf.urls.defaults import *

urlpatterns = patterns("memberships.views",

    # memberships
    url(r"^$", "membership_index", name="membership.index"),
    url(r"^search/$", "membership_search", name="membership.search"),
    url(r"^memberships/(?P<id>\d+)/$", "membership_details", name="membership.details"),

    # notices
    (r'^notices/', include('memberships.notices.urls')),

    # import
    url(r"^import/$", "membership_import", name="membership_import"),
    url(r"^import/upload-file/$", "membership_import", kwargs={'step':(1,'upload-file')}, name="membership_import_upload_file"),
    url(r"^import/map-fields/$", "membership_import", kwargs={'step':(2,'map-fields')}, name="membership_import_map_fields"),
    url(r"^import/preview/$", "membership_import", kwargs={'step':(3,'preview')}, name="membership_import_preview"),
    url(r"^import/confirm/$", "membership_import", kwargs={'step':(4,'confirm')}, name="membership_import_confirm"),

    # reports
    url(r'^reports/$', 'membership_join_report', name='reports-memberships-joins'),
    url(r'^reports/pdf/$', 'membership_join_report_pdf', name='reports-memberships-joins-pdf'),

    # entries
    url(r"^entries/$", "application_entries", name="membership.application_entries"),
    url(r"^entries/(?P<id>\d+)/$", "application_entries", name="membership.application_entries"),
    url(r"^entries/search/$", "application_entries_search", name="membership.application_entries_search"),

    # notice
    url(r"^notices/(?P<id>\d+)/email_content/$", "notice_email_content", name="membership.notice_email_content"),

    # application
    url(r"^confirmation/(?P<hash>[\w]+)/$", "application_confirmation", name="membership.application_confirmation"),
    url(r"^(?P<slug>[\w\-]+)/(?P<cmb_id>\d+)?/?$", "application_details", name="membership.application_details"),
    url(r"^(?P<slug>[\w\-]+)/corp-pre/(?P<cmb_id>\d+)?/?$", "application_details_corp_pre", name="membership.application_details_corp_pre"),
)
