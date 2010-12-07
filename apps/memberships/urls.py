from django.conf.urls.defaults import *

urlpatterns = patterns("memberships.views",
    url(r"^confirmation/(?P<hash>[\w]+)/$", "application_confirmation", name="membership.application_confirmation"),

    url(r"^entries/$", "application_entries", name="membership.application_entries"),
    url(r"^entries/(?P<id>\d+)/$", "application_entries", name="membership.application_entries"),

    url(r"^entries/search/$", "application_entries_search", name="membership.application_entries_search"),
    url(r"^approve-entry/(?P<id>\d+)/$", "approve_entry", name="membership.approve_entry"),
    url(r"^(?P<slug>[\w\-\/]+)/$", "application_details", name="membership.application_details"),
)


