# -*- coding: utf-8 -*-

import os.path
import warnings
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.six import string_types
from tendenci.apps.theme.templatetags.static import static

PYBB_TOPIC_PAGE_SIZE = getattr(settings, 'PYBB_TOPIC_PAGE_SIZE', 10)
PYBB_FORUM_PAGE_SIZE = getattr(settings, 'PYBB_FORUM_PAGE_SIZE', 20)
PYBB_AVATAR_WIDTH = getattr(settings, 'PYBB_AVATAR_WIDTH', 80)
PYBB_AVATAR_HEIGHT = getattr(settings, 'PYBB_AVATAR_HEIGHT', 80)
PYBB_MAX_AVATAR_SIZE = getattr(settings, 'PYBB_MAX_AVATAR_SIZE', 1024 * 50)
PYBB_DEFAULT_TIME_ZONE = getattr(settings, 'PYBB_DEFAULT_TIME_ZONE', -6)

PYBB_SIGNATURE_MAX_LENGTH = getattr(settings, 'PYBB_SIGNATURE_MAX_LENGTH', 1024)
PYBB_SIGNATURE_MAX_LINES = getattr(settings, 'PYBB_SIGNATURE_MAX_LINES', 3)

PYBB_DEFAULT_MARKUP = getattr(settings, 'PYBB_DEFAULT_MARKUP', 'bbcode')
PYBB_FREEZE_FIRST_POST = getattr(settings, 'PYBB_FREEZE_FIRST_POST', False)

PYBB_ATTACHMENT_SIZE_LIMIT = getattr(settings, 'PYBB_ATTACHMENT_SIZE_LIMIT', 1024 * 1024)
PYBB_ATTACHMENT_ENABLE = getattr(settings, 'PYBB_ATTACHMENT_ENABLE', False)
PYBB_ATTACHMENT_UPLOAD_TO = getattr(settings, 'PYBB_ATTACHMENT_UPLOAD_TO', os.path.join('pybb_upload', 'attachments'))

PYBB_DEFAULT_AVATAR_URL = getattr(settings, 'PYBB_DEFAULT_AVATAR_URL',
                                  static('pybb/img/default_avatar.jpg'))

PYBB_DEFAULT_TITLE = getattr(settings, 'PYBB_DEFAULT_TITLE', 'Tendenci with PYBB Open Source Forum')

PYBB_SMILES_PREFIX = getattr(settings, 'PYBB_SMILES_PREFIX', 'pybb/emoticons/')

PYBB_SMILES = getattr(settings, 'PYBB_SMILES', {
    '&gt;_&lt;': 'angry.png',
    ':.(': 'cry.png',
    'o_O': 'eyes.png',
    '[]_[]': 'geek.png',
    '8)': 'glasses.png',
    ':D': 'lol.png',
    ':(': 'sad.png',
    ':O': 'shok.png',
    '-_-': 'shy.png',
    ':)': 'smile.png',
    ':P': 'tongue.png',
    ';)': 'wink.png'
})

PYBB_NICE_URL = getattr(settings, 'PYBB_NICE_URL', False)
PYBB_NICE_URL_PERMANENT_REDIRECT = getattr(settings, 'PYBB_NICE_URL_PERMANENT_REDIRECT', True)
PYBB_NICE_URL_SLUG_DUPLICATE_LIMIT = getattr(settings, 'PYBB_NICE_URL_SLUG_DUPLICATE_LIMIT', 100)

# TODO In a near future, this code will be deleted when callable settings will not supported anymore.
callable_warning = ('%(setting_name)s should not be a callable anymore but a path to the parser classes.'
                    'ex : myproject.markup.CustomBBCodeParser. It will stop working in next pybbm release.')
wrong_setting_warning = ('%s setting will be removed in next pybbm version. '
                         'Place your custom quote functions in markup class and override '
                         'PYBB_MARKUP_ENGINES_PATHS/PYBB_MARKUP settings')
bad_function_warning = '%(bad)s function is deprecated. Use %(good)s instead.'


def getsetting_with_deprecation_check(all_settings, setting_name):
    setting_value = getattr(all_settings, setting_name)
    values = setting_value if type(setting_value) is not dict else setting_value.values()
    for value in values:
        if isinstance(value, string_types):
            continue
        warnings.warn(
            callable_warning % {'setting_name': setting_name, },
            DeprecationWarning
        )
    return setting_value


if not hasattr(settings, 'PYBB_MARKUP_ENGINES_PATHS'):
    PYBB_MARKUP_ENGINES_PATHS = {'bbcode': 'tendenci.apps.forums.markup.bbcode.BBCodeParser',
                                 'markdown': 'tendenci.apps.forums.markup.markdown.MarkdownParser'}
else:
    PYBB_MARKUP_ENGINES_PATHS = getattr(settings, 'PYBB_MARKUP_ENGINES_PATHS')

# TODO in the next major release : delete PYBB_MARKUP_ENGINES and PYBB_QUOTE_ENGINES settings
if not hasattr(settings, 'PYBB_MARKUP_ENGINES'):
    PYBB_MARKUP_ENGINES = PYBB_MARKUP_ENGINES_PATHS
else:
    warnings.warn(wrong_setting_warning % 'PYBB_MARKUP_ENGINES', DeprecationWarning)
    PYBB_MARKUP_ENGINES = getsetting_with_deprecation_check(settings, 'PYBB_MARKUP_ENGINES')

if not hasattr(settings, 'PYBB_QUOTE_ENGINES'):
    PYBB_QUOTE_ENGINES = PYBB_MARKUP_ENGINES_PATHS
else:
    warnings.warn(wrong_setting_warning % 'PYBB_QUOTE_ENGINES', DeprecationWarning)
    PYBB_QUOTE_ENGINES = getsetting_with_deprecation_check(settings, 'PYBB_QUOTE_ENGINES')

PYBB_MARKUP = getattr(settings, 'PYBB_MARKUP', None)
if not PYBB_MARKUP or PYBB_MARKUP not in PYBB_MARKUP_ENGINES:
    if not PYBB_MARKUP_ENGINES:
        warnings.warn('There is no markup engines defined in your settings. '
                      'Default pybb.base.BaseParser will be used.'
                      'Please set correct PYBB_MARKUP_ENGINES_PATHS and PYBB_MARKUP settings.',
                      DeprecationWarning)
        PYBB_MARKUP = None
    elif 'bbcode' in PYBB_MARKUP_ENGINES:
        # Backward compatibility. bbcode is the default markup
        PYBB_MARKUP = 'bbcode'
    else:
        raise ImproperlyConfigured('PYBB_MARKUP must be defined to an existing key of '
                                   'PYBB_MARKUP_ENGINES_PATHS')

PYBB_TEMPLATE = getattr(settings, 'PYBB_TEMPLATE', "forums_base.html")
PYBB_DEFAULT_AUTOSUBSCRIBE = getattr(settings, 'PYBB_DEFAULT_AUTOSUBSCRIBE', True)
PYBB_ENABLE_ANONYMOUS_POST = getattr(settings, 'PYBB_ENABLE_ANONYMOUS_POST', False)
PYBB_ANONYMOUS_USERNAME = getattr(settings, 'PYBB_ANONYMOUS_USERNAME', 'Anonymous')
PYBB_ANONYMOUS_VIEWS_CACHE_BUFFER = getattr(settings, 'PYBB_ANONYMOUS_VIEWS_CACHE_BUFFER', 100)

PYBB_DISABLE_SUBSCRIPTIONS = getattr(settings, 'PYBB_DISABLE_SUBSCRIPTIONS', False)
PYBB_DISABLE_NOTIFICATIONS = getattr(settings, 'PYBB_DISABLE_NOTIFICATIONS', False)
PYBB_PREMODERATION = getattr(settings, 'PYBB_PREMODERATION', False)

if not hasattr(settings, 'PYBB_BODY_CLEANERS'):
    PYBB_BODY_CLEANERS = ['tendenci.apps.forums.markup.base.rstrip_str', 'tendenci.apps.forums.markup.base.filter_blanks']
else:
    PYBB_BODY_CLEANERS = getsetting_with_deprecation_check(settings, 'PYBB_BODY_CLEANERS')

PYBB_BODY_VALIDATOR = getattr(settings, 'PYBB_BODY_VALIDATOR', None)

PYBB_POLL_MAX_ANSWERS = getattr(settings, 'PYBB_POLL_MAX_ANSWERS', 10)

PYBB_AUTO_USER_PERMISSIONS = getattr(settings, 'PYBB_AUTO_USER_PERMISSIONS', True)

PYBB_USE_DJANGO_MAILER = getattr(settings, 'PYBB_USE_DJANGO_MAILER', False)

PYBB_PERMISSION_HANDLER = getattr(settings, 'PYBB_PERMISSION_HANDLER', 'tendenci.apps.forums.permissions.CustomPermissionHandler')

PYBB_PROFILE_RELATED_NAME = getattr(settings, 'PYBB_PROFILE_RELATED_NAME', 'pybb_profile')

PYBB_INITIAL_CUSTOM_USER_MIGRATION = getattr(settings, 'PYBB_INITIAL_CUSTOM_USER_MIGRATION', None)

# Backward compatibility : define old functions which was defined here if some devs did used it
# TODO in a near future : delete those functions

def bbcode(s):
    warnings.warn(
        bad_function_warning % {
            'bad': 'tendenci.apps.forums.defaults.bbcode',
            'good': 'pytendenci.apps.forums.markup.bbcode.BBCodeParser',
        },
        DeprecationWarning)
    from .markup.bbcode import BBCodeParser

    return BBCodeParser().format(s)


def markdown(s):
    warnings.warn(
        bad_function_warning % {
            'bad': 'tendenci.apps.forums.defaults.markdown',
            'good': 'tendenci.apps.forums.markup.markdown.MarkdownParser',
        },
        DeprecationWarning)
    from .markup.markdown import MarkdownParser

    return MarkdownParser().format(s)


def _render_quote(name, value, options, parent, context):
    warnings.warn('pybb.defaults._render_quote function is deprecated. '
                  'This function is internal of new pybb.markup.bbcode.BBCodeParser class.',
                  DeprecationWarning)
    from .markup.bbcode import BBCodeParser

    return BBCodeParser()._render_quote(name, value, options, parent, context)


def smile_it(s):
    warnings.warn(
        bad_function_warning % {
            'bad': 'tendenci.apps.forums.defaults.smile_it',
            'good': 'tendenci.apps.forums.markup.base.smile_it',
        },
        DeprecationWarning)
    from .markup.base import smile_it as real_smile_it

    return real_smile_it(s)
