from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import User

from .models import UnPushedItem
from tendenci.apps.memberships.models import MembershipDefault


def save_unpushed_items(sender, **kwargs):
    """
    Enqueue or save items to be pushed to Authentik.
    """
    instance = kwargs['instance']
    deleted = kwargs.get('deleted', False)

    if sender is User:
        user = instance
    else:
        user = instance.user
    params = {
            'user_id': user.id,
        }
    if 'deleted' in kwargs or not user.membershipdefault_set.filter(status_detail='active').exists():
        params.update({
            'deleted': deleted
        })

    if not UnPushedItem.objects.filter(**params).exists():
        UnPushedItem.objects.create(**params)

def save_unpushed_items_for_delete(sender, **kwargs):
    kwargs['deleted'] = True
    save_unpushed_items(sender, **kwargs)


def init_signals():
    # When a membership is created or the status is changed, the associated user needs to be pushed to or removed from Authentik
    post_save.connect(save_unpushed_items, sender=MembershipDefault, weak=False)
    pre_delete.connect(save_unpushed_items, sender=MembershipDefault, weak=False)
    pre_delete.connect(save_unpushed_items_for_delete, sender=User, weak=False)

    