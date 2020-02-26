# -*- coding: utf-8 -*-


import os
import warnings
import uuid

from importlib import import_module
from django.utils.six import string_types
from django.utils.translation import ugettext as _
from . import compat

from .compat import get_username_field, get_user_model
from .defaults import (
    PYBB_MARKUP, PYBB_MARKUP_ENGINES_PATHS,
    PYBB_MARKUP_ENGINES, PYBB_QUOTE_ENGINES
)
from .markup.base import BaseParser

# TODO in the next major release : delete _MARKUP_ENGINES_FORMATTERS and _MARKUP_ENGINES_QUOTERS
_MARKUP_ENGINES = {}
_MARKUP_ENGINES_FORMATTERS = {}
_MARKUP_ENGINES_QUOTERS = {}

deprecated_func_warning = ('Deprecated function. Please configure correctly the PYBB_MARKUP_ENGINES_PATHS and'
                           'use get_markup_engine().%(replace)s() instead of %(old)s()(content).'
                           'In the next major release, this function will be deleted.')


def resolve_class(name):
    """ resolves a class function given as string, returning the function """
    if not name:
        return None
    modname, funcname = name.rsplit('.', 1)
    return getattr(import_module(modname), funcname)()


def resolve_function(path):
    if path:
        path = path.split('.')
        to_import = path.pop()
        module = import_module('.'.join(path))
        if module:
            return getattr(module, to_import)
    return None


def get_markup_engine(name=None):
    """
    Returns the named markup engine instance, or the default one if name is not given.
    This function will replace _get_markup_formatter and _get_markup_quoter in the
    next major release.
    """
    name = name or PYBB_MARKUP
    engine = _MARKUP_ENGINES.get(name)
    if engine:
        return engine
    if name not in PYBB_MARKUP_ENGINES_PATHS:
        engine = BaseParser()
    else:
        engine = PYBB_MARKUP_ENGINES[name]
        # TODO In a near future, we should stop to support callable
        if isinstance(engine, string_types):
            # This is a path, import it
            engine = resolve_class(engine)
    _MARKUP_ENGINES[name] = engine
    return engine


# TODO In the next major release, delete this function
def _get_markup_formatter(name=None):
    """
    Returns the named parse engine, or the default parser if name is not given.
    """
    warnings.warn(deprecated_func_warning % {'replace': 'format', 'old': '_get_markup_formatter'},
                  DeprecationWarning)
    name = name or PYBB_MARKUP

    engine = _MARKUP_ENGINES_FORMATTERS.get(name)
    if engine:
        return engine
    if name not in PYBB_MARKUP_ENGINES:
        engine = BaseParser().format
    else:
        engine = PYBB_MARKUP_ENGINES[name]
        if isinstance(engine, string_types):
            # This is a path, import it
            engine = resolve_class(engine).format

    _MARKUP_ENGINES_FORMATTERS[name] = engine
    return engine


# TODO In the next major release, delete this function
def _get_markup_quoter(name=None):
    """
    Returns the named quote engine, or the default quoter if name is not given.
    """
    warnings.warn(deprecated_func_warning % {'replace': 'quote', 'old': '_get_markup_quoter'},
                  DeprecationWarning)
    name = name or PYBB_MARKUP

    engine = _MARKUP_ENGINES_QUOTERS.get(name)
    if engine:
        return engine

    if name not in PYBB_QUOTE_ENGINES:
        engine = BaseParser().quote
    else:
        engine = PYBB_QUOTE_ENGINES[name]
        if isinstance(engine, string_types):
            # This is a path, import it
            engine = resolve_class(engine).quote

    _MARKUP_ENGINES_QUOTERS[name] = engine
    return engine


def get_body_cleaner(name):
    return resolve_function(name) if isinstance(name, string_types) else name


def unescape(text):
    """
    Do reverse escaping.
    """
    escape_map = [('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'), ('&quot;', '"'), ('&#39;', '\'')]
    for escape_values in escape_map:
        text = text.replace(*escape_values)
    return text


def get_pybb_profile(user):
    from . import defaults
    from .models import Profile

    if not user.is_authenticated:
        if defaults.PYBB_ENABLE_ANONYMOUS_POST:
            user = get_user_model().objects.get(**{get_username_field(): defaults.PYBB_ANONYMOUS_USERNAME})
        else:
            raise ValueError(_('Can\'t get profile for anonymous user'))

    if defaults.PYBB_PROFILE_RELATED_NAME and hasattr(user, defaults.PYBB_PROFILE_RELATED_NAME):
        return getattr(user, defaults.PYBB_PROFILE_RELATED_NAME)
    else:
        return Profile.objects.create(**{'user': user})


def get_pybb_profile_model():
    from . import defaults

    if defaults.PYBB_PROFILE_RELATED_NAME:
        return compat.get_related_model_class(get_user_model(), defaults.PYBB_PROFILE_RELATED_NAME)
    else:
        return get_user_model()


def build_cache_key(key_name, **kwargs):
    if key_name == 'anonymous_topic_views':
        return 'pybbm_anonymous_topic_%s_views' % kwargs['topic_id']
    else:
        raise ValueError('Wrong key_name parameter passed: %s' % key_name)


class FilePathGenerator(object):
    """
    Special class for generating random filenames
    Can be deconstructed for correct migration
    """

    def __init__(self, to, *args, **kwargs):
        self.to = to

    def deconstruct(self, *args, **kwargs):
        return 'tendenci.apps.forums.util.FilePathGenerator', [], {'to': self.to}

    def __call__(self, instance, filename):
        """
        This function generate filename with uuid4
        it's useful if:
        - you don't want to allow others to see original uploaded filenames
        - users can upload images with unicode in filenames wich can confuse browsers and filesystem
        """
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), ext)
        return os.path.join(self.to, filename)
