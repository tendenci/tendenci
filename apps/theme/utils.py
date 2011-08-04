import os
from django.conf import settings
from site_settings.utils import get_setting

def get_theme():
    theme = get_setting('module', 'theme_editor', 'theme')
    return theme

def get_theme_root():
    theme = get_setting('module', 'theme_editor', 'theme')
    theme_root = os.path.join(settings.THEME_DIR, theme)
    return theme_root

def theme_options():
    """
    Returns a string of the available themes in THEME_DIR
    """
    options = ''
    for theme in os.listdir(settings.THEME_DIR):
        options = '%s, %s' % (theme, options)
    print options[:-2]
    return options[:-2]
    
def theme_choices():
    """
    Returns a list of available themes in THEME_DIR
    """
    for theme in os.listdir(settings.THEME_DIR):
        yield theme
