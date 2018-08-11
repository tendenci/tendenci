import os
import configparser
from warnings import warn
from collections import deque
from io import StringIO

from django.conf import settings
from django.core.cache import cache

from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.theme.middleware import get_current_request


def get_active_theme():
    return get_setting('module', 'theme_editor', 'theme')

def get_theme(active_theme=None):
    if active_theme is None:
        active_theme = get_active_theme()
    request = get_current_request()
    if request:
        return request.session.get('theme', active_theme)
    return active_theme

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
    Returns a list of available themes in
    ORIGINAL_THEMES_DIR
    """
#     themes_dir = settings.BUILTIN_THEMES_DIR
#     for theme in os.listdir(themes_dir):
#         # Ignore '.' '..' and hidden directories
#         if theme.startswith('.'):
#             continue
#         if os.path.isdir(os.path.join(themes_dir, theme)):
#             yield 'builtin/'+theme
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

def is_base_theme(theme):
    return (get_theme_info(theme).get('General', {}).get('extends', None) == '')


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

    # Only cache if DEBUG is disabled
    if not settings.DEBUG:
        cache.set(cache_key, theme_info)

    return theme_info


def get_theme_search_order(theme=None):
    if theme is None:
        theme = get_theme()

    cache_key = '.'.join([settings.SITE_CACHE_KEY, 'theme_search_order', str(theme)])
    theme_search_order = cache.get(cache_key)
    if theme_search_order is not None:
        return theme_search_order

    if not os.path.isdir(get_theme_root(theme)):
        themes = [t for t in theme_choices()]
        if not themes:
            raise RuntimeError('No themes found')
        new_theme = themes[-1]
        warn('Theme "%s" does not exist, using "%s" instead'%(theme, new_theme))
        theme = new_theme

    # To support advanced/creative uses of theme inheritance, such as app-specific themes that can
    # be mixed and matched, support multiple inheritance via a comma-separated 'extends' list, and
    # collect themes in an appropriate order by performing a breadth-first tree traversal.
    search_order = []
    queue = deque([theme])
    seen = set()
    while queue:
        theme = queue.popleft()
        search_order.append(theme)
        extends = get_theme_info(theme).get('General', {}).get('extends', None)
        if extends == '':
            # Theme does not extend any other themes
            continue
        if extends is None:
            # For backward compatibility, we must assume that themes with no
            # 'extends' value should extend t7-base
            warn('Theme "%s" does not have an "extends" value, using "t7-base"'%(theme))
            extends = ['t7-base']
        else:
            extends = [e.strip() for e in extends.split(',')]
        builtin = is_builtin_theme(theme)
        theme_name = (get_builtin_theme_dir(theme) if builtin else theme)
        for next_theme in extends:
            # Determine whether extended theme is non-builtin, builtin, or non-existent, and add
            # 'builtin/' prefix if appropriate
            next_builtin = is_builtin_theme(next_theme)
            next_theme_name = (get_builtin_theme_dir(next_theme) if next_builtin else next_theme)
            if builtin:
                # If extending theme is builtin, only extend other builtin themes, to ensure that
                # the builtin themes always behave as expected
                if next_theme_name == theme_name:
                    warn('Theme "%s" extends itself'%(theme))
                    continue
                if not os.path.isdir(os.path.join(settings.BUILTIN_THEMES_DIR, next_theme_name)):
                    warn('Theme "%s" extends non-existent theme "%s"'%(theme, next_theme))
                    continue
                if not next_builtin:
                    next_theme = 'builtin/'+next_theme
            elif next_builtin:
                # If 'builtin/' prefix was explicitly specified in 'extends', only extend builtin
                # theme
                if not os.path.isdir(os.path.join(settings.BUILTIN_THEMES_DIR, next_theme_name)):
                    warn('Theme "%s" extends non-existent theme "%s"'%(theme, next_theme))
                    continue
            elif next_theme_name == theme_name:
                # If non-builtin theme extends itself, extend the builtin version instead
                if not os.path.isdir(os.path.join(settings.BUILTIN_THEMES_DIR, next_theme_name)):
                    warn('Theme "%s" extends non-existent builtin theme "%s"'%(theme, next_theme))
                    continue
                next_theme = 'builtin/'+next_theme
            elif not os.path.isdir(os.path.join(settings.ORIGINAL_THEMES_DIR, next_theme_name)):
                # If extending theme is non-builtin, extend non-builtin theme if available, or
                # extend builtin theme otherwise
                if not os.path.isdir(os.path.join(settings.BUILTIN_THEMES_DIR, next_theme_name)):
                    warn('Theme "%s" extends non-existent theme "%s"'%(theme, next_theme))
                    continue
                next_theme = 'builtin/'+next_theme
            if next_theme in seen:
                continue
            seen.add(next_theme)
            queue.append(next_theme)

    # Only cache if DEBUG is disabled
    if not settings.DEBUG:
        cache.set(cache_key, search_order)

    return search_order
