from django.contrib.auth import logout
from django.conf import settings
from django.contrib.auth.models import User

from tendenci.core.site_settings.utils import get_setting


class ProfileMiddleware(object):
    """
        Appends a profile instance to anonymous users.
        Creates a profile for logged in users without one.
    """
    def process_request(self, request):
        from tendenci.apps.profiles.models import Profile
        if request.user.is_anonymous():
            request.user.profile = Profile(status=False, status_detail="inactive", user=User(is_staff=False, is_superuser=False, is_active=False))
        else:
            try:
                profile = request.user.get_profile()
            except Profile.DoesNotExist:
                profile = Profile.objects.create_profile(user=request.user)


class ProfileLanguageMiddleware(object):
    """This middleware should come before django's LocaleMiddleware
    """
    if settings.USE_I18N:
        def get_user_language(self, request):
            try:
                lang =  getattr(request.user.profile, 'language')
            except:
                lang = None

            if not lang:
                lang = get_setting('site', 'global', 'localizationlanguage')
            return lang

        def process_request(self, request):
            """check user language and assign it to session or cookie accordingly
            """
            user_language = self.get_user_language(request)
            if user_language:
                if hasattr(request, 'session'):
                    lang_code_in_session = request.session.get('django_language', None)
                    if not lang_code_in_session or lang_code_in_session != user_language:
                        request.session['django_language'] = user_language
                else:
                    lang_code_in_cookie = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
                    if lang_code_in_cookie and lang_code_in_cookie != user_language:
                        request.COOKIES[settings.LANGUAGE_COOKIE_NAME] = user_language

        def process_response(self, request, response):
            """assign user_language to cookie LANGUAGE_COOKIE_NAME
            """
            user_language = self.get_user_language(request)
            lang_code_in_cookie = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
            if user_language and (not lang_code_in_cookie or user_language != lang_code_in_cookie):
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_language)
            return response


class ForceLogoutProfileMiddleware(object):
    def process_request(self, request):

        # this will force logout deactivated user on next request
        if request.user.is_authenticated():
            if not request.user.is_active:
                logout(request)