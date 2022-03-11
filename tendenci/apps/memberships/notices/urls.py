from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r"^logs/search/$", views.membership_notice_log_search, name="membership.notice.log.search"),
    re_path(r"^logs/(?P<id>\d+)/$", views.membership_notice_log_view, name="membership.notice.log.view"),
]
