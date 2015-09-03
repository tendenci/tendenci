# coding=utf-8
from __future__ import unicode_literals
import django
from django.conf import settings
from django.utils.encoding import force_text
from unidecode import unidecode


def get_image_field_class():
    try:
        from sorl.thumbnail import ImageField
    except ImportError:
        from django.db.models import ImageField
    return ImageField


def get_image_field_full_name():
    try:
        from sorl.thumbnail import ImageField
        name = 'sorl.thumbnail.fields.ImageField'
    except ImportError:
        from django.db.models import ImageField
        name = 'django.db.models.fields.files.ImageField'
    return name


def get_user_model():
    if django.VERSION[:2] >= (1, 5):
        from django.contrib.auth import get_user_model
        return get_user_model()
    else:
        from django.contrib.auth.models import User
        User.get_username = lambda u: u.username  # emulate new 1.5 method
        return User


def get_user_model_path():
    if django.VERSION[:2] >= (1, 5):
        return getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
    else:
        return 'auth.User'


def get_username_field():
    if django.VERSION[:2] >= (1, 5):
        return get_user_model().USERNAME_FIELD
    else:
        return 'username'


def get_atomic_func():
    try:
        from django.db.transaction import atomic as atomic_func
    except ImportError:
        from django.db.transaction import commit_on_success as atomic_func
    return atomic_func


def get_paginator_class():
    try:
        from pure_pagination import Paginator
        pure_pagination = True
    except ImportError:
        # the simplest emulation of django-pure-pagination behavior
        from django.core.paginator import Paginator, Page
        class PageRepr(int):
            def querystring(self):
                return 'page=%s' % self
        Page.pages = lambda self: [PageRepr(i) for i in range(1, self.paginator.num_pages + 1)]
        pure_pagination = False

    return Paginator, pure_pagination


def is_installed(app_name):
    if django.VERSION[:2] < (1, 7):
        from django.db.models import get_apps
        return app_name in get_apps()
    else:
        from django.apps import apps
        return apps.is_installed(app_name)


def get_related_model_class(parent_model, field_name):
    if django.VERSION[:2] < (1, 8):
        return getattr(parent_model, field_name).related.model
    else:
        return parent_model._meta.get_field(field_name).related_model


def slugify(text):
    """
    Slugify function that supports unicode symbols
    :param text: any unicode text
    :return: slugified version of passed text
    """
    if django.VERSION[:2] < (1, 5):
        from django.template.defaultfilters import slugify as django_slugify
    else:
        from django.utils.text import slugify as django_slugify

    return django_slugify(force_text(unidecode(text)))
