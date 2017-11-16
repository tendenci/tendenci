from __future__ import print_function
from django.db.models.signals import post_syncdb
from django.conf import settings
from django.utils.translation import ugettext_noop as _

if "tendenci.apps.notifications" in settings.INSTALLED_APPS:
    from tendenci.apps.notifications import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type(
                    "corp_memb_added",
                    _("Corporate Membership Added"),
                    _("A corporate membership has been added."))
        notification.create_notice_type(
                    "corp_memb_added_user",
                    _("Corporate Membership Added User Notice"),
                    _("A corporate membership has been added " + \
                      "- notice to user."))
        notification.create_notice_type(
                    "corp_memb_edited",
                    _("Corporate Membership Edited"),
                    _("A corporate membership  has been edited."))
        notification.create_notice_type(
                    "corp_memb_renewed",
                    _("Corporate Membership Renewed"),
                    _("A corporate membership has been renewed."))
        notification.create_notice_type(
                    "corp_memb_renewed_user",
                    _("Corporate Membership Renewal User Notice"),
                    _("A corporate membership has been renewed " + \
                      "- notice to user."))
        notification.create_notice_type(
                    "corp_memb_join_approved",
                    _("Corporate Membership Approved"),
                    _("A new corporate membership has been approved."))
        notification.create_notice_type(
                    "corp_memb_renewal_approved",
                    _("Corporate Membership Renewal Approved"),
                    _("The corporate membership renewal has been approved."))
        notification.create_notice_type(
                    "corp_memb_paid",
                    _("Payment Received for Corporate Membership"),
                    _("Payment for a corporate membership has been received."))
        notification.create_notice_type(
                    "corp_memb_notice_email",
                    _("Corporate Membership Notice Email"),
                    _("Custom Notice for Corporate Memberships"))

    post_syncdb.connect(create_notice_types, sender=notification)
else:
    print("Corporate Memberships: Skipping creation of NoticeTypes as notification app not found")
