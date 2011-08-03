import os
from django.conf import settings
from site_settings.utils import get_setting

def get_theme():
    theme = get_setting('site', 'global', 'theme')
    return theme

def get_theme_root():
    theme = get_setting('site', 'global', 'theme')
    theme_root = os.path.join(settings.THEME_DIR, theme)
    return theme_root
