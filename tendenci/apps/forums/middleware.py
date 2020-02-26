# -*- coding: utf-8 -*-


from django.utils import translation
from django.utils.deprecation import MiddlewareMixin

from .models import Profile


class PybbMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            profile, created  = Profile.objects.get_or_create(**{'user': request.user})

            if not profile.language:
                profile.language = translation.get_language_from_request(request)
                profile.save()

            request.session['django_language'] = profile.language
            translation.activate(profile.language)
            request.LANGUAGE_CODE = translation.get_language()
