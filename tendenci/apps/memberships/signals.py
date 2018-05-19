from django.db.models.signals import post_save, post_delete
from django.utils.translation import ugettext_noop as _
from tendenci.apps.memberships.models import MembershipDefault, MembershipApp
from tendenci.apps.contributions.signals import save_contribution
from tendenci.apps.notifications import models as notification


def check_and_update_membs_app_id(sender, **kwargs):
    my_app = kwargs['instance']

    if not my_app.status:
        switch_memberships_app_id(my_app)


def update_membs_app_id(sender, **kwargs):
    app_to_be_deleted = kwargs['instance']
    switch_memberships_app_id(app_to_be_deleted)


def switch_memberships_app_id(app_from):
    # each membership has an app_id associated.
    # since this app is to be deleted, we need to update memberships
    # with an available app_id
    app = MembershipApp.objects.exclude(id=app_from.id)
    if app_from.use_for_corp:
        app = app.filter(use_for_corp=True)
    app = app.filter(status=True, status_detail__in=('published', 'active'))
    [app] = app.order_by('-id')[:1] or [None]

    if app:
        MembershipDefault.objects.filter(app_id=app_from.id).update(app=app)


def create_notice_types(sender, **kwargs):
    verbosity = kwargs.get('verbosity', 2)
    notification.create_notice_type(
        "user_welcome",
        _("User Welcome"),
        _("User Account Created, Welcome Message"),
        verbosity=verbosity)

    notification.create_notice_type(
        'membership_joined_to_member',
        _('Membership Entry Submission'),
        _('Membership Entry Submission'),
        verbosity=verbosity)

    notification.create_notice_type(
        'membership_joined_to_admin',
        _('Membership Entry Submission'),
        _('Membership Entry Submission'),
        verbosity=verbosity)

    notification.create_notice_type(
        'membership_renewed_to_member',
        _('Membership Entry Renewal'),
        _('Membership Entry Renewal'),
        verbosity=verbosity)

    notification.create_notice_type(
        'membership_renewed_to_admin',
        _('Membership Entry Renewal'),
        _('Membership Entry Renewal'),
        verbosity=verbosity)

    notification.create_notice_type(
        'membership_approved_to_admin',
        _('Membership Application Approved'),
        _('Membership Application Approved'),
        verbosity=verbosity)

    notification.create_notice_type(
        'membership_disapproved_to_admin',
        _('Membership Application Disapproved'),
        _('Membership Application Disapproved'),
        verbosity=verbosity)

    notification.create_notice_type(
        'membership_approved_to_member',
        _('Membership Application Approved'),
        _('Membership Application Approved'),
        verbosity=verbosity)

    notification.create_notice_type(
        'membership_disapproved_to_member',
        _('Membership Application Disapproved'),
        _('Membership Application Disapproved'),
        verbosity=verbosity)

    notification.create_notice_type(
        'membership_notice_email',
        _('Membership Notice Email'),
        _('Membership Notice Custom Email'),
        verbosity=verbosity)

    notification.create_notice_type(
        'membership_corp_indiv_verify_email',
        _('Membership Corp Indiv Verify Email'),
        _('Membership Corp Indiv Email To Be Verified'),
        verbosity=verbosity)


def init_signals():
    post_save.connect(save_contribution, sender=MembershipDefault, weak=False)
    post_delete.connect(update_membs_app_id, sender=MembershipApp, weak=False)
    post_save.connect(check_and_update_membs_app_id, sender=MembershipApp, weak=False)
