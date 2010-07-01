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
    