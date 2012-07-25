from django.conf.urls.defaults import *


urlpatterns = patterns("tendenci.apps.subscribers.views",
    url(r"^(?P<id>\d+)/$", "subscribers", name="subscribers"),
    url(r"^detail/(?P<id>\d+)/$", "subscriber_detail", name="subscriber_detail"),
    url(r"^delete/(?P<id>\d+)/$", "subscriber_delete", name="subscriber_delete"),
)
