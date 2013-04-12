import os
from django.conf import settings
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


def get_theme_template(template_name, theme=None):
    """Returns a relative path for the theme template.
    This is used primarily as an input for loader's get_template
    """
    if theme is None:  # default theme
        theme = get_theme()
    theme_template = template_name
    return theme_template


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
