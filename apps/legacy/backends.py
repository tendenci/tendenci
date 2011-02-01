from django.contrib.auth.models import User

from models import SchipulEmployee
from models import LegacyUser
from utils import get_profile_defaults, legacy_user_is_developer, legacy_user_is_admin
from profiles.utils import user_add_remove_admin_auth_group

import hashlib

class LegacyUserBackend(object):
    """
    backend used to authenticate users against a MSSQL legacy user table

    Possible reasons why a login could fail:
    
    1. Password does not match on the django or legacy database
    2. Username was not found on the django and legacy database
    3. Username contains spaces on the legacy database
    4. Username from legacy database is too long for the django database
       30 character max
    5. Username has already been copied down and creating the user would
       cause duplicates (very rare, but possible. Usually happens if
       the backends are not in correct order in AUTHENTICATION_BACKENDS
    """
    def create_user_from_legacy(self, legacy_user):
        """
        Create a new django user from the information
        provided by the legacy database.

        Users passed to this method are already assumed:
        interactive = 1
        status = 1
        statusdetail = 'active'
        """
        # create the user
        user = User()
        user.username = legacy_user.username
        user.set_password(legacy_user.password)
        user.first_name = legacy_user.firstname
        user.last_name = legacy_user.lastname
        user.email = legacy_user.email
        user.is_active = True
        user.is_staff = False
        user.is_superuser = False

        # test for legacy user rights and adjust accordingly
        if legacy_user_is_developer(legacy_user):
            user.is_staff = True
            user.is_superuser = True
            
        if legacy_user_is_admin(legacy_user):
            user.is_staff = True
            user.is_superuser = False

        try:
            user.save()
        except: # most likely a duplicate username, send back failure
            return None

        # if they are an administrator then add them to the auth group "Admin"
        user_add_remove_admin_auth_group(user)

        # create the profile, whole lotta fields
        profile_defaults = get_profile_defaults(legacy_user)
        profile_defaults.update({
            'allow_anonymous_view': False,
            'allow_user_view': False,
            'allow_member_view': False,
            'allow_anonymous_edit': False,
            'allow_user_edit': False,
            'allow_member_edit': False,
            'creator': user,
            'creator_username': user.username,
            'owner': user,
            'owner_username': user.username,
            'status': True,
            'status_detail': 'active'
        })
        try:
            user.profile.create(**profile_defaults)
        except:
            return user # send success so django can continue processing
        return user

    def login_local_user(self, username, password):
        """
        Original Django code for logging in
        Local = Tendenci 5 database
        """
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
            else:
                return None
        except User.DoesNotExist:
            return None

    def login_legacy_user(self, username, password, model_class=LegacyUser, use_hash=True):
        """
        Login a user from a legacy Tendenci database
        """
        from re import search
        try:
            # this query is pulling using a .filter() query because for some reason
            # when you use .get() it causes an error when connecting to the
            # MSSQL database. It seems like a bug in pyodbc using django-pyodbc
            # I spent some time using PDB and stepping through the code
            # but couldn't find any reason for it to do this since .get()
            # actually calls .filter() behind the scenes. Need enlightenment.
            default_lookups = {
                'username': username,
                'interactive': 1,
                'status': 1,
                'statusdetail': 'active'
            }
            legacy_user = model_class.objects.filter(**default_lookups)[0]
        except:
            return None # user doesn't exists that satisfies default_lookup, send back failure

        # username is too long for the django users table, invalid
        if len(legacy_user.username) > 30:
            return None
        # username contains a space, invalid
        if search(r'\s+', legacy_user.username):
            return None

        if use_hash:
            password = hashlib.md5(password).hexdigest()
            
        if password == legacy_user.password:
            user = self.create_user_from_legacy(legacy_user)
            return user
        return None # user was found but passwords didn't match, send back failure

    def authenticate(self, username=None, password=None):
        """
        Authenticate against the Legacy T4 users table
        """
        user = self.login_local_user(username, password)
        if not user:
            user = self.login_legacy_user(username, password)
            return user
        return user # return None and continue to the next backend
        
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class MasterUserBackend(LegacyUserBackend):
    """
    backend used to authenticate users against MSSQL master
    user table for employee master login to the site

    MSSQL server: NTSERVER28
    Database: tendencistats
    """
    def authenticate(self, username=None, password=None):
        # check for the a master login
        # accepted logins are: schipul\username and schipul/username
        user = None
        prefix = ''
        username_fs = username.split('\\')
        username_bs = username.split('/')
        
        if len(username_fs) == 2:
            prefix, username = username_fs
        if len(username_bs) == 2:
            prefix, username = username_bs

        # Check to see if this is a master login
        # if so, take the following steps:
        #
        # 1. Check the local database first
        #    -- if the username exists, test password
        #       -- if password fails prompt user with failure message
        #       -- if password succeeds login
        #
        # 2. If local database user doesn't exist, check master (MSSQL - NTSERVER29)
        #    -- if the username exists, test password
        #       -- if password fails prompt user with failure message
        #       -- if password succeeds, copy down user and login
        #    -- if username doesn't exist prompt user with failure message
        #
        # Note: once the user is copied down they should only ever go through step 1
        if prefix.lower() == 'schipul':
            user = self.login_local_user(username, password)
            if not user:
                model_class = SchipulEmployee
                user = self.login_legacy_user(username, password, model_class=model_class, use_hash=False)
            return user
        return user # return None and continue to the next backend