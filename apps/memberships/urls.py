from django.conf.urls.defaults import *

urlpatterns = patterns("memberships.views",

    # memberships
    url(r"^memberships/(?P<id>\d+)/$", "membership_details", name="membership.details"),
    url(r"^memberships/import_csv/$", "import_membership_csv", name="import_membership_csv"),
    
    # entries
    url(r"^entries/$", "application_entries", name="membership.application_entries"),
    url(r"^entries/(?P<id>\d+)/$", "application_entries", name="membership.application_entries"),
    url(r"^entries/search/$", "application_entries_search", name="membership.application_entries_search"),

    # application
    url(r"^confirmation/(?P<hash>[\w]+)/$", "application_confirmation", name="membership.application_confirmation"),
    url(r"^(?P<slug>[\w\-]+)/(?P<cmb_id>\d+)?/?$", "application_details", name="membership.application_details"),
    url(r"^(?P<slug>[\w\-]+)/corp-pre/(?P<cmb_id>\d+)?/?$", "application_details_corp_pre", name="membership.application_details_corp_pre"),
    
)
