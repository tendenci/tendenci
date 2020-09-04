from urllib.parse import urlparse, parse_qs
import time
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.views import LogoutView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views import View
from django.urls import reverse

from authlib.integrations.django_client import OAuth

from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.site_settings.utils import get_setting


oauth = OAuth()

remote_app_name = settings.OAUTH2_REMOTE_APP_NAME

oauth.register(
    name=remote_app_name,
    client_id=settings.OAUTH2_CLIENT_ID,
    client_secret=settings.OAUTH2_CLIENT_SECRET,
    userinfo_endpoint=settings.OAUTH2_USERINFO_ENDPOINT,
    access_token_url=settings.OAUTH2_ACCESS_TOKEN_URL,
    access_token_params=settings.OAUTH2_ACCESS_TOKEN_PARAMS,
    authorize_url=settings.OAUTH2_AUTHORIZE_URL,
    authorize_params=settings.OAUTH2_AUTHORIZE_PARAMS,
    api_base_url=settings.OAUTH2_API_BASE_URL,
    client_kwargs=settings.OAUTH2_CLIENT_KWARGS,
)

myclient = oauth.create_client(settings.OAUTH2_REMOTE_APP_NAME)


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect(request.GET.get('next', settings.LOGIN_REDIRECT_URL))

        request.session['next'] = request.GET.get('next', settings.LOGIN_REDIRECT_URL)

        redirect_uri = '{site_url}{callback_url}'.format(
                                site_url=get_setting('site', 'global', 'siteurl'),
                                callback_url=reverse('oauth2_auth'))
        auth_redirect = myclient.authorize_redirect(request, redirect_uri)

        # Save state in session
        url = auth_redirect.url
        query = urlparse(url).query
        request.session['oauth2_login_state'] = parse_qs(query)['state'][0]

        return auth_redirect


class AuthorizeView(View):
    def get(self, request):
        # Check code and state and if the state received matches with the one sent
        if 'state' in request.GET and 'code' in request.GET and \
            request.GET['state'] == request.session.get('oauth2_login_state'):
            del  request.session['oauth2_login_state']
    
            token = myclient.authorize_access_token(request)
            
            #user = get_user(user_info, create=True)
            user = auth.authenticate(request, myclient=myclient, token=token)
            if user:
                #request.user = user
                auth.login(request, user)

                # Calculate the time (in sec) the session expires in
                expires_in = int(token.get('expires_in', 0))
                if 'expires_at' in token:
                    expires_at = int(token.get('expires_at', 0))
                    session_expires_in = min([expires_in, expires_at - int(time.time())])
                else:
                    session_expires_in = expires_in

                # Set session to expire in session_expires_in
                request.session.set_expiry(session_expires_in)
                EventLog.objects.log(instance=request.user, application="oauth2")
    
                redirect_to = request.session.pop('next', settings.LOGIN_REDIRECT_URL)

                return HttpResponseRedirect(redirect_to)
    
        return HttpResponseRedirect(settings.LOGIN_URL) 


class Oauth2LogoutView(LogoutView):
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            auth_logout(request)
            
            if hasattr(settings, 'OAUTH2_LOGOUT_REDIRECT_URL') and settings.OAUTH2_LOGOUT_REDIRECT_URL:
                # Log out from oauth2 logout endpoint provider
                next_page = '{url}?client_id={client_id}&logout_uri={site_url}{logout_url}'.format(
                                url=settings.OAUTH2_LOGOUT_REDIRECT_URL,
                                client_id=settings.OAUTH2_CLIENT_ID,
                                site_url=get_setting('site', 'global', 'siteurl'),
                                logout_url=reverse('oauth2_logout'))

                return HttpResponseRedirect(next_page)
        return super(Oauth2LogoutView, self).dispatch(request, *args, **kwargs)    
