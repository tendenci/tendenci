from django.db.models.signals import post_syncdb
from django.utils.translation import ugettext_noop as _

from tendenci.apps.notifications import models as notification


def create_notice_types(app, created_models, verbosity, **kwargs):

    notification.create_notice_type(
        "user_welcome",
        _("User Welcome"),
        _("User Account Created, Welcome Message"))

    notification.create_notice_type(
        'membership_joined_to_member',
        _('Membership Entry Submission'),
        _('Membership Entry Submission'))

    notification.create_notice_type(
        'membership_joined_to_admin',
        _('Membership Entry Submission'),
        _('Membership Entry Submission'))

    notification.create_notice_type(
        'membership_renewed_to_member',
        _('Membership Entry Renewal'),
        _('Membership Entry Renewal'))

    notification.create_notice_type(
        'membership_renewed_to_admin',
        _('Membership Entry Renewal'),
        _('Membership Entry Renewal'))

    notification.create_notice_type(
        'membership_approved_to_admin',
        _('Membership Application Approved'),
        _('Membership Application Approved'))

    notification.create_notice_type(
        'membership_disapproved_to_admin',
        _('Membership Application Disapproved'),
        _('Membership Application Disapproved'))

    notification.create_notice_type(
        'membership_approved_to_member',
        _('Membership Application Approved'),
        _('Membership Application Approved'))

    notification.create_notice_type(
        'membership_disapproved_to_member',
        _('Membership Application Disapproved'),
        _('Membership Application Disapproved'))

    notification.create_notice_type(
        'membership_corp_indiv_verify_email',
        _('Membership Corp Indiv Verify Email'),
        _('Membership Corp Indiv Email To Be Verified'))

post_syncdb.connect(create_notice_types, sender=notification)
