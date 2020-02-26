
from django.utils.translation import ugettext_noop as _

from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.user_groups.models import Group, GroupMembership
from tendenci.apps.notifications import models as notification

def create_notice_types(sender, **kwargs):
    verbosity = kwargs.get('verbosity', 2)
    notification.create_notice_type(
                "corp_memb_added",
                _("Corporate Membership Added"),
                _("A corporate membership has been added."),
                verbosity=verbosity)
    notification.create_notice_type(
                "corp_memb_added_user",
                _("Corporate Membership Added User Notice"),
                _("A corporate membership has been added " +
                  "- notice to user."),
                verbosity=verbosity)
    notification.create_notice_type(
                "corp_memb_edited",
                _("Corporate Membership Edited"),
                _("A corporate membership  has been edited."),
                verbosity=verbosity)
    notification.create_notice_type(
                "corp_memb_renewed",
                _("Corporate Membership Renewed"),
                _("A corporate membership has been renewed."),
                verbosity=verbosity)
    notification.create_notice_type(
                "corp_memb_renewed_user",
                _("Corporate Membership Renewal User Notice"),
                _("A corporate membership has been renewed " +
                  "- notice to user."),
                verbosity=verbosity)
    notification.create_notice_type(
                "corp_memb_join_approved",
                _("Corporate Membership Approved"),
                _("A new corporate membership has been approved."),
                verbosity=verbosity)
    notification.create_notice_type(
                "corp_memb_renewal_approved",
                _("Corporate Membership Renewal Approved"),
                _("The corporate membership renewal has been approved."),
                verbosity=verbosity)
    notification.create_notice_type(
                "corp_memb_paid",
                _("Payment Received for Corporate Membership"),
                _("Payment for a corporate membership has been received."),
                verbosity=verbosity)
    notification.create_notice_type(
                "corp_memb_notice_email",
                _("Corporate Membership Notice Email"),
                _("Custom Notice for Corporate Memberships"),
                verbosity=verbosity)


def get_reps_group():
    group_id = get_setting('module', 'corporate_memberships', 'corpmembershiprepsgroupid')
    reps_group = None
    if group_id:
        try:
            [reps_group] = Group.objects.filter(id=int(group_id))[:1] or [None]
        except:
            reps_group = None
    return reps_group

def add_rep_to_group(sender, instance=None, created=False, **kwargs):
    if instance and created:
        reps_group = get_reps_group()
        if reps_group:
            user = instance.user
            if not reps_group.is_member(user):
                reps_group.add_user(user)

def remove_rep_from_group(sender, instance=None, **kwargs):
    if instance:
        reps_group = get_reps_group()
        if reps_group:
            user = instance.user
            if reps_group.is_member(user):
                gm = GroupMembership.objects.get(group=reps_group,
                                                 member=user)
                gm.delete()

def init_signals():
    from django.db.models.signals import post_save, pre_delete
    from tendenci.apps.corporate_memberships.models import CorpMembership, CorpMembershipRep
    from tendenci.apps.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=CorpMembership, weak=False)
    reps_group = get_reps_group()
    if reps_group:
        post_save.connect(add_rep_to_group, sender=CorpMembershipRep, weak=False)
        pre_delete.connect(remove_rep_from_group, sender=CorpMembershipRep, weak=False)
