from django.conf.urls.defaults import *

urlpatterns = patterns("tendenci.addons.corporate_memberships.notices.views",
    url(r"^logs/search/$", "corporate_membership_notice_log_search", name="corporate_membership.notice.log.search"),
    url(r"^logs/(?P<id>\d+)/$", "corporate_membership_notice_log_view", name="corporate_membership.notice.log.view"),
)
