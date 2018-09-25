import os

from django.conf import settings
from django.conf.urls import include, url


def update_addons(installed_apps, addon_folder_path):
    # Append only enabled addons to the INSTALLED_APPS
    addons = get_addons(installed_apps, addon_folder_path)
    installed_addons = tuple([i for i in addons])
    installed_apps += installed_addons

    return installed_apps


def get_addons(installed_apps, addon_folder_path):
    """
    Grabs a list of apps that aren't in INSTALLED_APPS
    """
    new_addons = []

    custom_addons = sorted(custom_choices(addon_folder_path))
    for addon in custom_addons:
        addon_package = '.'.join(['addons', addon])
        try:
            __import__(addon_package)
            new_addons.append(addon_package)
        except ImportError:
            pass

    return new_addons


def custom_choices(addon_folder_path):
    """
    Returns a list of available addons in the tendenci-site wrapper app
    """
    for addon in os.listdir(addon_folder_path):
        if os.path.isdir(os.path.join(addon_folder_path, addon)) and addon not in ['__pycache__']:
            yield addon


def get_url_patterns():
    items = []
    addons = get_addons(settings.INSTALLED_APPS, settings.SITE_ADDONS_PATH)
    for addon in addons:
        try:
            __import__('.'.join([addon, 'urls']))
            items.append(url(r'', include('%s.urls' % addon,)))
        except ImportError:
            pass
    return items
