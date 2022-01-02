from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r"^logs/search/$", views.corporate_membership_notice_log_search, name="corporate_membership.notice.log.search"),
    re_path(r"^logs/(?P<id>\d+)/$", views.corporate_membership_notice_log_view, name="corporate_membership.notice.log.view"),
]
