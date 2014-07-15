from tendenci.core.site_settings.utils import get_setting
from tendenci.apps.user_groups.models import Group, GroupMembership

group_id = get_setting('module', 'corporate_memberships', 'corpmembershiprepsgroupid')
reps_group = None
if group_id:
    [reps_group] = Group.objects.filter(id=int(group_id))[:1] or [None]

def add_rep_to_group(sender, instance=None, created=False, **kwargs):
    if instance and created:
        if reps_group:
            user = instance.user
            if not reps_group.is_member(user):
                reps_group.add_user(user)

def remove_rep_from_group(sender, instance=None, **kwargs):
    if instance:
        if reps_group:
            user = instance.user
            if reps_group.is_member(user):
                gm = GroupMembership.objects.get(group=reps_group,
                                                 member=user)
                gm.delete()

def init_signals():
    from django.db.models.signals import post_save, pre_delete
    from tendenci.addons.corporate_memberships.models import CorpMembership, CorpMembershipRep
    from tendenci.apps.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=CorpMembership, weak=False)
    if reps_group:
        post_save.connect(add_rep_to_group, sender=CorpMembershipRep, weak=False)
        pre_delete.connect(remove_rep_from_group, sender=CorpMembershipRep, weak=False)
