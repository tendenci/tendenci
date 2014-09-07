"""
Facebook OAuth support.

This contribution adds support for Facebook OAuth service. The Settings
FACEBOOK_APP_ID and FACEBOOK_API_SECRET must be defined with the values
given by Facebook application registration process.

Extended permissions are supported by defining FACEBOOK_EXTENDED_PERMISSIONS
setting, it must be a list of values to request.

By default account id and token expiration time are stored in extra_data
field, check OAuthBackend class for details on how to extend it.
"""
import cgi
import urllib

from django.conf import settings
import simplejson
from django.contrib.auth import authenticate

from tendenci.apps.social_auth.backends import BaseOAuth, OAuthBackend, USERNAME

from tendenci.apps.site_settings.models import Setting
from tendenci.apps.site_settings.utils import get_setting

# Facebook configuration
FACEBOOK_SERVER = 'graph.facebook.com'
FACEBOOK_AUTHORIZATION_URL = 'https://%s/oauth/authorize' % FACEBOOK_SERVER
FACEBOOK_ACCESS_TOKEN_URL = 'https://%s/oauth/access_token' % FACEBOOK_SERVER
FACEBOOK_CHECK_AUTH = 'https://%s/me' % FACEBOOK_SERVER
EXPIRES_NAME = getattr(settings, 'SOCIAL_AUTH_EXPIRATION', 'expires')


class FacebookBackend(OAuthBackend):
    """Facebook OAuth authentication backend"""
    name = 'facebook'
    # Default extra data to store
    EXTRA_DATA = [('id', 'id'), ('expires', EXPIRES_NAME)]

    def get_user_details(self, response):
        """Return user details from Facebook account"""
        return {USERNAME: response['name'],
                'email': response.get('email', ''),
                'fullname': response['name'],
                'first_name': response.get('first_name', ''),
                'last_name': response.get('last_name', '')}


class FacebookAuth(BaseOAuth):
    """Facebook OAuth mechanism"""
    AUTH_BACKEND = FacebookBackend
    
    def __init__(self, request, redirect):
        self.FACEBOOK_APP_ID = get_setting(scope='module', scope_category='users', name='facebook_app_id')
        self.FACEBOOK_API_SECRET = get_setting(scope='module', scope_category='users', name='facebook_api_secret')
        super(FacebookAuth, self).__init__(request, redirect)
    
    def auth_url(self):
        """Returns redirect url"""
        args = {'client_id': self.FACEBOOK_APP_ID,
                'redirect_uri': self.redirect_uri}
        if hasattr(settings, 'FACEBOOK_EXTENDED_PERMISSIONS'):
            args['scope'] = ','.join(settings.FACEBOOK_EXTENDED_PERMISSIONS)
        return FACEBOOK_AUTHORIZATION_URL + '?' + urllib.urlencode(args)
    
    def auth_complete(self, *args, **kwargs):
        """Returns user, might be logged in"""
        if 'code' in self.data:
            url = FACEBOOK_ACCESS_TOKEN_URL + '?' + \
                  urllib.urlencode({'client_id': self.FACEBOOK_APP_ID,
                                'redirect_uri': self.redirect_uri,
                                'client_secret': self.FACEBOOK_API_SECRET,
                                'code': self.data['code']})
            response = cgi.parse_qs(urllib.urlopen(url).read())
            access_token = response['access_token'][0]
            data = self.user_data(access_token)
            if data is not None:
                if 'error' in data:
                    error = self.data.get('error') or 'unknown error'
                    raise ValueError('Authentication error: %s' % error)
                data['access_token'] = access_token
                # expires will not be part of response if offline access
                # premission was requested
                if 'expires' in response:
                    data['expires'] = response['expires'][0]
            kwargs.update({'response': data, FacebookBackend.name: True})
            return authenticate(*args, **kwargs)
        else:
            error = self.data.get('error') or 'unknown error'
            raise ValueError('Authentication error: %s' % error)

    def user_data(self, access_token):
        """Loads user data from service"""
        params = {'access_token': access_token,}
        url = FACEBOOK_CHECK_AUTH + '?' + urllib.urlencode(params)
        try:
            return simplejson.load(urllib.urlopen(url))
        except ValueError:
            return None

    @classmethod
    def enabled(cls):
        """Return backend enabled status by checking Setting Model"""
        try:
            FACEBOOK_APP_ID = get_setting(scope='module', scope_category='users', name='facebook_app_id')
            FACEBOOK_API_SECRET = get_setting(scope='module', scope_category='users', name='facebook_api_secret')
        except Setting.DoesNotExist:
            return False
        return True

# Backend definition
BACKENDS = {
    'facebook': FacebookAuth,
}
