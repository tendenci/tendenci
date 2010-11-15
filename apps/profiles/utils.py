from site_settings.utils import get_setting

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
    
    auth_groups = Auth_Group.objects.filter(name=name)
    
    return auth_groups

def user_add_remove_admin_auth_group(user, auth_group=None):
    """
        if user is admin and not on admin auth group, add them.
        if user is not admin but on admin auth group, remove them
    """
    if user.is_staff and (not user.is_superuser):   # they are admin
        if auth_group:
            auth_group_list = [auth_group]
        else:
            auth_group_list = get_admin_auth_group()
        
        if auth_group_list:
            if not user.id: # new user
                user.groups = auth_group_list
                user.save()
                
            else:           # existing user
                add_to_auth_group = True
                user_edit_auth_groups = user.groups.all()
                if user_edit_auth_groups:
                    if user_edit_auth_groups[0] == auth_group_list[0]:
                        add_to_auth_group = False
                        
                if add_to_auth_group:
                    user.groups = [auth_group_list[0]]
                    user.save()
                    
    else:
        if user.id:
            user.groups = []
            user.save()
        