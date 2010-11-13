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
    
    
def get_admin_auth_group(name="Admin"):
    from django.contrib.auth.models import Group as Auth_Group
    
    auth_groups = Auth_Group.objects.filter(name=name)
    
    return auth_groups