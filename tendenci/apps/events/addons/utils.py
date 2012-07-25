from datetime import datetime
import operator
from django.db.models import Q

from django.contrib.auth.models import User, AnonymousUser

from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.events.models import Event, Addon, AddonOption

def get_active_addons(event):
    """
    Returns all active addons of an event.
    """
    addons = Addon.objects.filter(event=event, status=True)
    return addons

def get_available_addons(event, user, is_strict=False):
    """
    Get the available addons of an event for user.
    """
    filter_and, filter_or = get_addon_access_filter(user, is_strict=is_strict)
    q_obj = None
    if filter_and:
        q_obj = Q(**filter_and)
    if filter_or:
        q_obj_or = reduce(operator.or_, [Q(**{key: value}) for key, value in filter_or.items()])
        if q_obj:
            q_obj = reduce(operator.and_, [q_obj, q_obj_or])
        else:
            q_obj = q_obj_or
            
    addons = Addon.objects.filter(
                event=event,
                status=True
                )
    if q_obj:
        addons = addons.filter(q_obj)
        
    return addons

def get_addon_access_filter(user, is_strict=False):
    if user.profile.is_superuser: return None, None
    
    filter_and, filter_or = None, None
    
    if is_strict:
        if user.is_anonymous():
            filter_or = {'allow_anonymous': True}
        elif not user.profile.is_member:
            filter_or = {'allow_anonymous': True,
                         'allow_user': True
                        }
        else:
            # user is a member
            filter_or = {'allow_anonymous': True,
                         'allow_user': True,
                         'allow_member': True}
            # get a list of groups for this user
            groups_id_list = user.group_member.values_list('group__id', flat=True)
            if groups_id_list:
                filter_or.update({'group__id__in': groups_id_list})
    else:
        filter_or = {'allow_anonymous': True,
                    'allow_user': True,
                    'allow_member': True,
                    'group__id__gt': 0}

            
    return filter_and, filter_or
    
    
    
def get_addons_for_list(event, users):
    """
    Returns the available addons of an event for a given list of users.
    """
    addons = Addon.objects.none()
    
    for user in users:
        addons = addons | get_available_addons(event, user)
    addons = addons | get_available_addons(event, AnonymousUser())
    
    # return the QUERYSET
    return addons
    
def can_use_addon(event, user, addon):
    """
    Determine if a user can use a specific addon of a given event
    """
    addons = get_available_addons(event, user)
    return addons.filter(pk=addon.pk).exists()
    
def create_regaddon(form, event, reg8n):
    """
    Create the RegAddon.
    form is a RegAddonForm with the specifed addon options.
    reg8n is the Registration instance to associate the regaddon with.
    """
    
    regaddon = RegAddon()
    
    return regaddon
    
