# coding=utf-8

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
        from django.db.models import ImageField  # noqa:F401
        name = 'django.db.models.fields.files.ImageField'
    return name


def get_user_model():
    from django.contrib.auth import get_user_model
    return get_user_model()


def get_user_model_path():
    return getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


def get_username_field():
    return get_user_model().USERNAME_FIELD


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
    from django.apps import apps
    return apps.is_installed(app_name)


def get_related_model_class(parent_model, field_name):
    return parent_model._meta.get_field(field_name).related_model


def slugify(text):
    """
    Slugify function that supports unicode symbols
    :param text: any unicode text
    :return: slugified version of passed text
    """
    from django.utils.text import slugify as django_slugify

    return django_slugify(force_text(unidecode(text)))
