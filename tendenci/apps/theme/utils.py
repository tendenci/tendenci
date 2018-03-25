import os
import configparser
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

def get_theme_root(theme=None):
    if theme is None:  # default theme
        theme = get_theme()
    return os.path.join(settings.ORIGINAL_THEMES_DIR, theme)

def theme_choices():
    """
    Returns a list of available themes in ORIGINAL_THEMES_DIR
    """
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


def prepend_file(filename, prep_text="[General]\n"):
    f = open(filename)
    text = f.read()
    f.close()
    # open the file again for writing
    f = open(filename, 'w')
    f.write(prep_text)
    # write the original contents
    f.write(text)
    f.close()

def get_theme_info(theme=None):
    """Returns a dict of the fields from the theme.info file for the theme.
    A dict is preferred so we can loop through the fields.

    """
    if not theme:
        theme = get_theme()

    cache_key = '.'.join([settings.CACHE_PRE_KEY, str(theme)])
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    theme_info = {}

    theme_info_file = os.path.join(get_theme_root(theme), 'theme.info')
    if os.path.isfile(theme_info_file):
        config = configparser.ConfigParser()
        try:
            config.read(theme_info_file)
        except configparser.MissingSectionHeaderError:
            prepend_file(theme_info_file)
            config.read(theme_info_file)
        # Get a dict of the fields, not the object itself.
        theme_info = config._sections

    # Only cache if DEBUG is disabled.
    if not settings.DEBUG:
        cache.set(cache_key, theme_info)

    return theme_info
