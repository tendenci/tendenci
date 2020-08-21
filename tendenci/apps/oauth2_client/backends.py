#from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.backends import RemoteUserBackend
from tendenci.apps.profiles.models import Profile

UserModel = get_user_model()


class AuthenticationBackend(RemoteUserBackend):
    """
    Authenticates against access token.
    """

    def authenticate(self, request=None, myclient=None, token=None, **kwargs):
        if myclient and token:
            user_info = myclient.userinfo(token=token)
    
            user = self.get_user_by_user_info(user_info=user_info)
    
            return user if self.user_can_authenticate(user) else None
    
    def get_user_by_user_info(self, user_info, create=True):
        if user_info:
            username = user_info.get(settings.OAUTH2_USER_ATTR_MAPPING.get('username', ''), None)
            if username:
                [user] = UserModel.objects.filter(username=username)[:1] or [None]
                if user and not user.is_active:
                    user.is_active = True
                    user.save()
        
                if not user and create:
                    user = UserModel(username=username)
                    user.set_unusable_password()
                    user.save()
                    Profile.objects.create_profile(user=user)

                self.sync_user(user, user_info)
                return user if self.user_can_authenticate(user) else None

        return None
    
    def sync_user(self, user, user_info):
        # Updated other user field
        updated = False
        for user_attr in settings.OAUTH2_USER_ATTR_MAPPING.keys():
            user_info_attr = settings.OAUTH2_USER_ATTR_MAPPING[user_attr]
            if user_attr != 'username':
                if hasattr(user, user_attr):
                    value = user_info.get(user_info_attr, '')
                    if value:
                        setattr(user, user_attr, value)
                        updated = True
        if updated:
            user.save()
            
    def clean_user_data(self):
        pass
        
