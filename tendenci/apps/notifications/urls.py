from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.notices, name="notification_notices"),
    url(r'^(\d+)/$', views.single, name="notification_notice"),
    url(r'^feed/$', views.feed_for_user, name="notification_feed_for_user"),
    url(r'^mark_all_seen/$', views.mark_all_seen, name="notification_mark_all_seen"),
    url(r'^(?P<guid>[\d\w-]+)?/$', views.email, name="notification_email"),
]
