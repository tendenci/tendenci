from django.conf.urls import url
from . import views

urlpatterns = [
    url(r"^logs/search/$", views.membership_notice_log_search, name="membership.notice.log.search"),
    url(r"^logs/(?P<id>\d+)/$", views.membership_notice_log_view, name="membership.notice.log.view"),
]
