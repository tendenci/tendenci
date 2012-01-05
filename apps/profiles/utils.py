from django.conf import settings
from site_settings.utils import get_setting
from user_groups.models import GroupMembership, Group
from memberships.models import Membership, App

def profile_edit_admin_notify(request, old_user, old_profile, profile, **kwargs):
    from django.core.mail.message import EmailMessage
    from django.template.loader import render_to_string
    from django.conf import settings
    from django.template import RequestContext
    
    subject = 'User Account Modification Notice for %s' % get_setting('site', 'global', 'sitedisplayname')
    body = render_to_string('profiles/edit_notice.txt', 
                               {'old_user':old_user,
                                'old_profile': old_profile, 
                                'profile': profile},
                               context_instance=RequestContext(request))
   
    sender = settings.DEFAULT_FROM_EMAIL
    recipients = ['%s<%s>' % (r[0], r[1]) for r in settings.ADMINS]
    msg = EmailMessage(subject, body, sender, recipients)
    msg.content_subtype = 'html'
    try:
        msg.send()
    except:
        pass
    
# return admin auth group as a list    
def get_admin_auth_group(name="Admin"):
    from django.contrib.auth.models import Group as Auth_Group
    
    try:
        auth_group = Auth_Group.objects.get(name=name)
    except Auth_Group.DoesNotExist:
        auth_group = Auth_Group(name=name)
        auth_group.save()
    
    return auth_group

def user_add_remove_admin_auth_group(user, auth_group=None):
    """
    if user is admin and not on admin auth group, add them.
    if user is not admin but on admin auth group, remove them
    """
    if user.is_staff and (not user.is_superuser):   # they are admin
        if not auth_group:
            if hasattr(settings, 'ADMIN_AUTH_GROUP_NAME'):
                auth_group_name = settings.ADMIN_AUTH_GROUP_NAME
            else:
                auth_group_name = 'Admin'
            auth_group = get_admin_auth_group(name=auth_group_name)
            
      
        if not user.id: # new user
            user.groups = [auth_group]
            user.save()
            
        else:           # existing user
            group_updated = False
            user_edit_auth_groups = user.groups.all()
            if user_edit_auth_groups:
                if auth_group not in user_edit_auth_groups:
                    user_edit_auth_groups.append(auth_group)
                    user.groups = user_edit_auth_groups
                    group_updated = True
            else:
                user.groups = [auth_group]
                group_updated = True
                    
            if group_updated:
                user.save()
                    
    else:
        if user.id:
            user.groups = []
            user.save()
        
def get_groups(user, filter=None):
    """
    Returns the groups of a given user.
    if filter is given it will filter the user's groups based on it.
    filter is assumed to be a QuerySet or a SearchQuerySet of Group.
    """
    memberships = GroupMembership.objects.filter(member=user)
    
    if filter:
        pks = [group.pk for group in filter]
        memberships = memberships.filter(group__pk__in = pks)
        
    groups = []
    for member in memberships:
        groups.append(member.group)
        
    return groups
    
def get_memberships(user, filter=None):
    """
    Returns the memberships of a given user.
    if filter is given it will filter the user's memberships based on it.
    filter is assumed to be a QuerySet or a SearchQuerySet of Group.
    """
    memberships = GroupMembership.objects.filter(member=user)
    
    if filter:
        pks = [group.pk for group in filter]
        memberships = memberships.filter(group__pk__in = pks)
        
    return memberships
    
def group_choices(user):
    """
    returns a list of (group.pk, group.label) for groups viewable
    for the given user.
    """
    groups = Group.objects.search(user=user)
    choices = [(group.pk, "%s (%s)" % (group.label, group.name)) for group in groups]
    
    return choices

def app_choices(user):
    """
    returns a list of (app.pk, app.name) for apps viewable for a given user.
    """
    apps = App.objects.search(user=user)
    choices = [(app.pk, app.name) for app in apps]
    
    return choices
