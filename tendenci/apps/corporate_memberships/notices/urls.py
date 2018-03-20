from django.conf.urls import url
from . import views

urlpatterns = [
    url(r"^logs/search/$", views.corporate_membership_notice_log_search, name="corporate_membership.notice.log.search"),
    url(r"^logs/(?P<id>\d+)/$", views.corporate_membership_notice_log_view, name="corporate_membership.notice.log.view"),
]
