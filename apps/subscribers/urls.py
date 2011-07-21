from django.conf.urls.defaults import *


urlpatterns = patterns("subscribers.views",
    url(r"^(?P<id>\d+)$", "subscribers", name="subscribers"),
    url(r"^delete/(?P<id>\d+)$", "subscriber_delete", name="subscriber_delete"),
)
