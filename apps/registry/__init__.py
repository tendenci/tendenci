from django.utils import importlib
from registry.sites import site
from django.contrib.admin import autodiscover as ad


# load the apps that are in Django Admin
ad()


def autodiscover():
    """
    Automatically build the registry for the apps that are in the system
    """
    import imp
    from django.conf import settings

    for app in settings.INSTALLED_APPS:
        # For each app, we need to look for a registry.py inside that app's
        try:
            app_path = importlib.import_module(app).__path__
        except AttributeError:
            continue

        # Step 2: use imp.find_module to find the app's registry.py
        try:
            imp.find_module('app_registry', app_path)
        except ImportError:
            continue

        # Step 3: import the app's registry file. Bubble up errors
        importlib.import_module("%s.app_registry" % app)

autodiscover()
