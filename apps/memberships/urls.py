from django.conf.urls.defaults import *

urlpatterns = patterns("memberships.views",
    url(r"^$", "membership_index", name="membership.index"),
    url(r"^search/$", "membership_search", name="membership.search"),

    (r'^notices/', include('memberships.notices.urls')),

    # memberships
    url(r"^memberships/(?P<id>\d+)/$", "membership_details", name="membership.details"),
    url(r"^memberships/import_csv/$", "import_membership_csv", name="import_membership_csv"),

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
