from django.conf.urls.defaults import *

urlpatterns = patterns("memberships.views",
    url(r"^confirmation/(?P<hash>[\w]+)/$", "application_confirmation", name="membership.application_confirmation"),
    url(r"^(?P<slug>[\w\-\/]+)/$", "application_details", name="membership.application_details"),
)


