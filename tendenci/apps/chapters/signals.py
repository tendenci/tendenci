from django.utils.translation import gettext_noop as _

from tendenci.apps.notifications import models as notification
from tendenci.apps.chapters.models import CoordinatingAgency


def create_chapter_membership_notice_types(sender, **kwargs):
    verbosity = kwargs.get('verbosity', 2)
    notification.create_notice_type(
        'chapter_membership_notice_email',
        _('Chapter Membership Notice Email'),
        _('Chapter Membership Notice Custom Email'),
        verbosity=verbosity)

    notification.create_notice_type(
        'chapter_membership_joined_to_admin',
        _('Chapter Membership Join Submission'),
        _('Chapter Membership Join Submission'),
        verbosity=verbosity)

    notification.create_notice_type(
        'chapter_membership_renewed_to_admin',
        _('Chapter Membership Entry Renewal'),
        _('Chapter Membership Entry Renewal'),
        verbosity=verbosity)


def add_member_to_coord_group(sender, **kwargs):
    """
    Add member to the corresponding chapter coordinator group (based on state) on member join.
    """
    membership = kwargs['instance']
    profile = membership.user.profile
    if profile.state:
        [c_agency] = CoordinatingAgency.objects.filter(state=profile.state)[:1] or [None]
        if c_agency:
            group = c_agency.group
            group.add_user(membership.user,
                         creator_id=membership.creator_id,
                         creator_username=membership.creator_username,
                         owner_id=membership.owner_id,
                         owner_username=membership.owner_username)