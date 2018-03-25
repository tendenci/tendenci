import os
import configparser
from io import StringIO

from django.conf import settings
from django.core.cache import cache

from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.theme.middleware import get_current_request


def get_active_theme():
    return get_setting('module', 'theme_editor', 'theme')

def get_theme():
    request = get_current_request()
    if request:
        return request.session.get('theme', get_active_theme())
    return get_active_theme()

def get_builtin_theme_dir(theme):
    return theme[len('builtin/'):]

def get_theme_root(theme=None):
    if theme is None:  # default theme
        theme = get_theme()
    if is_builtin_theme(theme):
        return os.path.join(settings.BUILTIN_THEMES_DIR, get_builtin_theme_dir(theme))
    return os.path.join(settings.ORIGINAL_THEMES_DIR, theme)


def theme_choices():
    """
    Returns a list of available themes in BUILTIN_THEMES_DIR and
    ORIGINAL_THEMES_DIR
    """
    themes_dir = settings.BUILTIN_THEMES_DIR
    for theme in os.listdir(themes_dir):
        # Ignore '.' '..' and hidden directories
        if theme.startswith('.'):
            continue
        if os.path.isdir(os.path.join(themes_dir, theme)):
            yield 'builtin/'+theme
    themes_dir = settings.ORIGINAL_THEMES_DIR
    for theme in os.listdir(themes_dir):
        # Ignore '.' '..' and hidden directories
        if theme.startswith('.'):
            continue
        if os.path.isdir(os.path.join(themes_dir, theme)):
            yield theme

def theme_options():
    """
    Returns a string of the available themes, for use in the theme_editor
    settings input_value.
    """
    options = ''
    for theme in sorted(theme_choices()):
        options += ', '+theme
    return options[2:]  # Remove first ', '


def is_valid_theme(theme):
    return (theme in theme_choices())

def is_builtin_theme(theme):
    return theme.startswith('builtin/')


def get_theme_info(theme=None):
    """Returns a dict of the fields from the theme.info file for the theme.
    A dict is preferred so we can loop through the fields.

    """
    if theme is None:
        theme = get_theme()

    cache_key = '.'.join([settings.SITE_CACHE_KEY, 'theme_info', str(theme)])
    theme_info = cache.get(cache_key)
    if theme_info is not None:
        return theme_info

    if is_builtin_theme(theme) or not settings.USE_S3_THEME:
        info_file = os.path.join(get_theme_root(theme), 'theme.info')
        if not os.path.isfile(info_file):
            return {}
        with open(info_file) as fp:
            info_str = fp.read()
    else:
        from tendenci.libs.boto_s3.utils import read_theme_file_from_s3
        info_str = read_theme_file_from_s3(os.path.join(theme, 'theme.info'))

    theme_info = configparser.ConfigParser()
    try:
        if hasattr(theme_info, 'read_string'):
            # Python 3.2
            theme_info.read_string(info_str, source='theme.info')
        else:
            theme_info.readfp(StringIO.StringIO(info_str), 'theme.info')
    except configparser.MissingSectionHeaderError:
        info_str = '[General]\n'+info_str
        if hasattr(theme_info, 'read_string'):
            theme_info.read_string(info_str, source='theme.info')
        else:
            theme_info.readfp(StringIO.StringIO(info_str), 'theme.info')

    # Return a dict of the fields rather than a ConfigParser object.
    # Note that ConfigParser._sections is undocumented and may not work in
    # future versions of Python.
    theme_info = theme_info._sections

    # Only cache if DEBUG is disabled.
    if not settings.DEBUG:
        cache.set(cache_key, theme_info)

    return theme_info
