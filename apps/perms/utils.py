from profiles.models import Profile
from django.contrib.auth.models import User

def is_admin(user):
    if not user or user.is_anonymous():
        return False
    
    if hasattr(user, 'is_admin'):
        return getattr(user, 'is_admin')
    else:
        try:
            profile = user.get_profile()
        except Profile.DoesNotExist:
            profile = Profile.objects.create_profile(user=user)
        if user.is_superuser and user.is_active and profile.status==1 \
                and profile.status_detail.lower()=='active':
            setattr(user, 'is_admin', True)
            return True
        else:
            setattr(user, 'is_admin', False)
            return False
        
def is_developer(user):
    if not user or user.is_anonymous():
        return False

    if hasattr(user, 'is_developer'):
        return getattr(user, 'is_developer')
    else:
        try:
            profile = user.get_profile()
        except Profile.DoesNotExist:
            profile = Profile.objects.create_profile(user=user)
        if user.is_superuser and user.is_staff and user.is_active \
                and profile.status==1 \
                and profile.status_detail.lower()=='active':
            setattr(user, 'is_developer', True)
            return True
        else:
            setattr(user, 'is_developer', False)
            return False

def get_administrators():
    return User.objects.filter(is_active=True,is_staff=True)

# get a list of the admin notice recipients
def get_notice_recipients(scope, scope_category, setting_name):
    from site_settings.utils import get_setting
    from django.core.validators import email_re
    
    recipients = []
    # global recipients
    g_recipients = (get_setting('site', 'global', 'allnoticerecipients')).split(',')
    g_recipients = [r.strip() for r in g_recipients]
    
    # module recipients
    m_recipients = (get_setting(scope, scope_category, setting_name)).split(',')
    m_recipients = [r.strip() for r in m_recipients]

    for recipient in list(set(g_recipients+m_recipients)):
        if email_re.match(recipient):
            recipients.append(recipient)
        
    return recipients
