import pytz

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core import exceptions

from tendenci.apps.profiles.models import Profile
from tendenci.apps.perms.backend import ObjectPermBackend

UserModel = get_user_model()


class AuthenticationBackend(ObjectPermBackend):
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
            username = self.clean_username(username)
            if username:
                [user] = UserModel.objects.filter(username=username)[:1] or [None]
                if user and not user.is_active:
                    user.is_active = True
                    user.save()
        
                if not user and create:
                    user = UserModel(username=username)
                    user.set_unusable_password()
                    user.save()
                    profile = Profile.objects.create_profile(user=user)
                elif user:
                    profile = getattr(user, 'profile', None)
                    if not profile:
                        profile = Profile.objects.create_profile(user=user)
                if user:
                    self.sync_user(user, user_info)
                    self.sync_user(profile, user_info, ObjModel=Profile)

                return user if self.user_can_authenticate(user) else None

        return None
    
    def sync_user(self, user, user_info, ObjModel=UserModel):
        """
        Updated other user and/or profile fields if needed.
        """
        fields_dict = {}
        for field in ObjModel._meta.fields:
            if field.name in settings.OAUTH2_USER_ATTR_MAPPING and hasattr(field, 'max_length'):
                fields_dict[field.name] = field
        
        updated = False
        for user_attr in settings.OAUTH2_USER_ATTR_MAPPING.keys():
            user_info_attr = settings.OAUTH2_USER_ATTR_MAPPING[user_attr]
            if user_attr != 'username':
                if hasattr(user, user_attr):
                    value = user_info.get(user_info_attr, '')
                    if value:
                        if user_attr in fields_dict:
                            # clean data
                            value = self.clean_data(value, fields_dict[user_attr], model_instance=user)
                            if value:
                                setattr(user, user_attr, value)
                                updated = True

        if updated:
            user.save()

    def clean_username(self, username):
        """
        Perform any cleaning on the "username" prior to using it to get or
        create the user object.  Return the cleaned username.
        """
        field = [field for field in UserModel._meta.fields if field.name=='username'][0]

        return self.clean_data(username, field)

    def clean_data(self, value, field, model_instance=None):
        """
        Clean the data ``value`` for the field.
        """
        field_type = field.get_internal_type()
        if field.name !='username' and field_type in ['CharField', 'EmailField',
                                                      'URLField', 'SlugField']:
            # if length is too long, truncate it. But not for username
            if len(value) > field.max_length:
                value = value[:field.max_length]
            if field.name == 'time_zone':
                if value not in pytz.all_timezones:
                    timezone_map = {'AST': 'Canada/Atlantic',
                                     'EST': 'US/Eastern',
                                     'CST': 'US/Central',
                                     'MST': 'US/Mountain',
                                     'AKST': 'US/Alaska',
                                     'PST': 'US/Pacific',
                                     'GMT': 'UTC'
                                     }
                    if value in timezone_map:
                        value = timezone_map[value]
                    else:
                        value = None

        # set to None if it doesn't pass the validation
        try:
            if model_instance:
                value = field.clean(value, model_instance)
            else:
                value = field.to_python(value)
                field.run_validators(value)
        except exceptions.ValidationError:
            value = None
        return value
