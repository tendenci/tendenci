# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import
from django.utils import translation
from django.db.models import ObjectDoesNotExist
from django.contrib.auth.models import Permission
from . import util
from tendenci.apps.site_settings.utils import get_setting

class PybbMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            try:
                # Here we try to load profile, but can get error
                # if user created during syncdb but profile model
                # under south control. (Like pybb.Profile).
                profile = util.get_pybb_profile(request.user)
            except ObjectDoesNotExist:
                # Ok, we should create new profile for this user
                # and grant permissions for add posts
                # It should be caused rarely, so we move import signal here
                # to prevent circular import
                from tendenci.apps.forums.signals import user_saved
                user_saved(request.user, created=True)
                profile = util.get_pybb_profile(request.user)

            if not profile.language:
                profile.language = translation.get_language_from_request(request)
                profile.save()

            request.session['django_language'] = profile.language
            translation.activate(profile.language)
            request.LANGUAGE_CODE = translation.get_language()

