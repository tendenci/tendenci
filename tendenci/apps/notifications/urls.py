from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.notices, name="notification_notices"),
    re_path(r'^(\d+)/$', views.single, name="notification_notice"),
    re_path(r'^feed/$', views.feed_for_user, name="notification_feed_for_user"),
    re_path(r'^mark_all_seen/$', views.mark_all_seen, name="notification_mark_all_seen"),
    re_path(r'^(?P<guid>[\d\w-]+)?/$', views.email, name="notification_email"),
]
