from django.contrib.auth import logout
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.deprecation import MiddlewareMixin

from tendenci.apps.site_settings.utils import get_setting


class ProfileMiddleware(MiddlewareMixin):
    """
        Appends a profile instance to anonymous users.
        Creates a profile for logged in users without one.
    """
    def process_request(self, request):
        from tendenci.apps.profiles.models import Profile
        if request.user.is_anonymous:
            request.user.profile = Profile(status=False, status_detail="inactive", user=User(is_staff=False, is_superuser=False, is_active=False))
        else:
            try:
                request.user.profile
            except Profile.DoesNotExist:
                Profile.objects.create_profile(user=request.user)


class ProfileLanguageMiddleware(MiddlewareMixin):
    """This middleware should come before django's LocaleMiddleware
    """
    if settings.USE_I18N:
        def get_user_language(self, request):
            try:
                lang =  getattr(request.user.profile, 'language').strip(' ')
            except:
                lang = None

            return lang or get_setting('site', 'global', 'localizationlanguage') or settings.LANGUAGE_CODE

        def process_request(self, request):
            """check user language and assign it to cookie
            """
            lang = self.get_user_language(request)

            request.COOKIES[settings.LANGUAGE_COOKIE_NAME] = lang

        def process_response(self, request, response):
            """assign user_language to cookie LANGUAGE_COOKIE_NAME
            """
            lang = self.get_user_language(request)
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)

            return response


class ForceLogoutProfileMiddleware(MiddlewareMixin):
    def process_request(self, request):

        # this will force logout deactivated user on next request
        if request.user.is_authenticated:
            if not request.user.is_active:
                logout(request)
