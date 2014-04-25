import os
import ConfigParser
from django.conf import settings
from django.core.cache import cache
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.theme.middleware import get_current_request


def get_theme():
    request = get_current_request()
    if request:
        theme = request.session.get('theme', get_setting('module', 'theme_editor', 'theme'))
    else:
        theme = get_setting('module', 'theme_editor', 'theme')
    return theme


def get_theme_root(theme=None):
    if theme is None:  # default theme
        theme = get_theme()
    if settings.USE_S3_THEME:
        theme_root = theme
    else:
        # local theme root
        theme_root = (os.path.join(settings.ORIGINAL_THEMES_DIR, theme)).replace('\\', '/')
    return theme_root


# this function is doing nothing and needs to be removed
def get_theme_template(template_name, theme=None):
    """Returns a relative path for the theme template.
    This is used primarily as an input for loader's get_template
    """
#     if theme is None:  # default theme
#         theme = get_theme()
#     theme_template = template_name
    return template_name


def theme_options():
    """
    Returns a string of the available themes in THEMES_DIR
    """
    options = ''
    themes = sorted(theme_choices())
    themes.reverse()
    for theme in themes:
        options = '%s, %s' % (theme, options)
    return options[:-2]


def theme_choices():
    """
    Returns a list of available themes in ORIGINAL_THEMES_DIR
    """
    themes_dir = settings.ORIGINAL_THEMES_DIR

    for theme in os.listdir(themes_dir):
        if os.path.isdir(os.path.join(themes_dir, theme)):
            # catch hidden directories
            if not theme.startswith('.'):
                yield theme


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

        config = ConfigParser.ConfigParser()
        try:
            config.read(os.path.join(theme_root, 'theme.info'))
        except ConfigParser.MissingSectionHeaderError:
            prepend_file(os.path.join(theme_root, 'theme.info'))
            config.read(os.path.join(theme_root, 'theme.info'))

        cached = config._sections

        # Only cache if DEBUG is disabled.
        if not settings.DEBUG:
            cache.set(key, cached)
    return cached
