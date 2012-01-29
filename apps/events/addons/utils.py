from datetime import datetime

from django.contrib.auth.models import User, AnonymousUser

from perms.utils import is_admin, is_member
from site_settings.utils import get_setting

from events.models import Event, Addon, AddonOption
    
def get_active_addons(event):
    """
    Returns all active addons of an event.
    """
    addons = Addon.objects.filter(event=event, status=True)
    return addons

def get_available_addons(event, user):
    """
    Returns the available addons of an event for a given user.
    """
    
    addons = get_active_addons(event)
    
    if is_admin(user):
        # return all if admin is user
        return addons
    
    if not user.is_authenticated():
        # public addons only
        addons = addons.filter(allow_anonymous=True)
    else:
        exclude_list = []
        # user permitted addons
        for addon in addons:
            # shown to all users
            if addon.allow_anonymous or addon.allow_user:
                continue
            
            # Members allowed
            if addon.allow_member and is_member(user):
                continue
            
            # Group members allowed
            if addon.group and addon.group.is_member(user):
                continue
            
            # user failed all permission checks
            exclude_list.append(addon.pk)
        # exclude addons user failed permission checks with
        addons = addons.exclude(pk__in=exclude_list)
    
    # return the QUERYSET
    return addons
    
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
    
