# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.utils import translation
from django.db.models import ObjectDoesNotExist
from django.contrib.auth.models import Permission
import util
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
            
            # if Self Registration is on, users can post on forums per Ed.
            # assign the add_post perm if user doesn't have it.
            if get_setting('module', 'users', 'selfregistration'):
                if not request.user.has_perm('forums.add_post'):
                    [perm] = Permission.objects.filter(
                                        content_type__app_label='forums',
                                        content_type__model='post',
                                        codename='add_post')[:1] or [None]
                    if perm:
                        request.user.user_permissions.add(perm)
