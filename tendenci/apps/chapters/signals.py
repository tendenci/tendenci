from django.utils.translation import gettext_noop as _

from tendenci.apps.notifications import models as notification


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