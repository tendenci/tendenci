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
    theme_root = get_theme_root(theme)
    keys = [settings.CACHE_PRE_KEY, str(theme)]
    key = '.'.join(keys)
    cached = cache.get(key)
    if cached is None:
        # Get a dict of the fields, not the object itself.

        config = configparser.ConfigParser()
        try:
            config.read(os.path.join(theme_root, 'theme.info'))
        except configparser.MissingSectionHeaderError:
            prepend_file(os.path.join(theme_root, 'theme.info'))
            config.read(os.path.join(theme_root, 'theme.info'))

        cached = config._sections

        # Only cache if DEBUG is disabled.
        if not settings.DEBUG:
            cache.set(key, cached)
    return cached
