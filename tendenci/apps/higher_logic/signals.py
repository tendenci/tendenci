from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import User

from tendenci.apps.higher_logic.models import UnPushedItem
from tendenci.apps.events.models import Registrant, Event, AssetsPurchase
from tendenci.apps.memberships.models import MembershipDefault
from tendenci.apps.staff.models import Staff
from tendenci.apps.profiles.models import Profile
from tendenci.apps.user_groups.models import GroupMembership


def save_unpushed_items(sender, **kwargs):
    """
    Enqueue or save items to be pushed to HL.
    """
    instance = kwargs['instance']
    deleted = kwargs.get('deleted', False)
    if sender in (User, Profile, Registrant, MembershipDefault, Staff, GroupMembership):        
        if sender is User:
            user = instance
        elif sender is Profile:
            profile = instance
            user = profile.user
        else:
            if sender is GroupMembership:
                user = instance.member
            else:
                user = instance.user

        if hasattr(user, 'profile'):
            profile = user.profile
        else:
            profile = None

        if profile and profile.account_id:
            identifier = profile.account_id       

            params = {
                'user_id': user.id,
                'identifier': identifier,
                'deleted': deleted
            }

            if not UnPushedItem.objects.filter(**params).exists():
                UnPushedItem.objects.create(**params)
    elif sender is Event:
        if not instance.parent:
            params = {
                    'event_id': instance.id,
                    'identifier': f'event-{instance.id}',
                    'deleted': deleted
            }
            if not UnPushedItem.objects.filter(**params).exists():
                UnPushedItem.objects.create(**params)


def save_unpushed_items_for_delete(sender, **kwargs):
    kwargs['deleted'] = True
    save_unpushed_items(sender, **kwargs)


def init_signals():
    for model in (Event, Profile, Registrant, AssetsPurchase, MembershipDefault, Staff, GroupMembership):
        # When these items are created or updated, the associated user needs to be updated as well at HL
        post_save.connect(save_unpushed_items, sender=model, weak=False)
    for model in (Registrant, AssetsPurchase, MembershipDefault, Staff, GroupMembership):
        # When these items are deleted, the associated user needs to be updated at HL
        pre_delete.connect(save_unpushed_items, sender=model, weak=False)
    for model in (User, Event):
        # When a user or an event is deleted from db, they need to be deleted at HL
        pre_delete.connect(save_unpushed_items_for_delete, sender=model, weak=False)

    