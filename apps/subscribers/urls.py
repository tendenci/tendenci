from django.conf.urls.defaults import *


urlpatterns = patterns("subscribers.views",
    url(r"^(?P<id>\d+)$", "subscribers", name="subscribers"),
    url(r"^delete/(?P<id>\d+)$", "delete_subscriber", name="delete_subscriber"),
)
