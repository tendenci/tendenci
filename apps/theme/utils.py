import os
from django.conf import settings
from site_settings.utils import get_setting

def get_theme():
    theme = get_setting('module', 'theme_editor', 'theme')
    return theme

def get_theme_root(theme=None):
    if theme is None: # default theme
        theme = get_theme()
    theme_root = os.path.join(settings.THEMES_DIR, theme)
    return theme_root
    
def get_theme_template(template_name, theme=None):
    if theme is None: # default theme
        theme = get_theme()
    theme_template = os.path.join(settings.PROJECT_ROOT, 'themes', theme, 'templates', template_name)
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
    Returns a list of available themes in THEMES_DIR
    """
    for theme in os.listdir(settings.THEMES_DIR):
        if os.path.isdir(os.path.join(settings.THEMES_DIR, theme)):
            yield theme
