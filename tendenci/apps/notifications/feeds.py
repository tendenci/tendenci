from datetime import datetime

from django.urls import reverse
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import linebreaks, escape, striptags
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.notifications.models import Notice
from tendenci.apps.notifications.atomformat import Feed


ITEMS_PER_FEED = getattr(settings, 'ITEMS_PER_FEED', 20)
DEFAULT_HTTP_PROTOCOL = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")


class BaseNoticeFeed(Feed):
    def item_id(self, notification):
        return "%s://%s%s" % (
            DEFAULT_HTTP_PROTOCOL,
            Site.objects.get_current().domain,
            notification.get_absolute_url(),
        )

    def item_title(self, notification):
        return striptags(notification.message)

    def item_updated(self, notification):
        return notification.added

    def item_published(self, notification):
        return notification.added

    def item_content(self, notification):
        return {"type" : "html", }, linebreaks(escape(notification.message))

    def item_links(self, notification):
        return [{"href" : self.item_id(notification)}]

    def item_authors(self, notification):
        return [{"name" : notification.user.username}]


class NoticeUserFeed(BaseNoticeFeed):
    def get_object(self, params):
        return get_object_or_404(User, username=params[0].lower())

    def feed_id(self, user):
        return "%s://%s%s" % (
            DEFAULT_HTTP_PROTOCOL,
            Site.objects.get_current().domain,
            reverse('notification_feed_for_user'),
        )

    def feed_title(self, user):
        return _('Notices Feed')

    def feed_updated(self, user):
        qs = Notice.objects.filter(user=user)
        # We return an arbitrary date if there are no results, because there
        # must be a feed_updated field as per the Atom specifications, however
        # there is no real data to go by, and an arbitrary date can be static.
        if qs.count() == 0:
            return datetime(year=2008, month=7, day=1)
        return qs.latest('added').added

    def feed_links(self, user):
        complete_url = "%s://%s%s" % (
            DEFAULT_HTTP_PROTOCOL,
            Site.objects.get_current().domain,
            reverse('notification_notices'),
        )
        return ({'href': complete_url},)

    def items(self, user):
        return Notice.objects.notices_for(user).order_by("-added")[:ITEMS_PER_FEED]
