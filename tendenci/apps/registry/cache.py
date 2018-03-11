from django.core.cache import cache
from django.conf import settings

REGISTRY_PRE_KEY = "registry"

def delete_reg_apps_cache():
    """Delete cache for all apps
    """
    keys = [settings.CACHE_PRE_KEY, REGISTRY_PRE_KEY, 'reg_apps']
    key = '.'.join(keys)
    cache.delete(key)

def cache_reg_apps(apps):
    """Caches the list of registered apps
    """
    keys = [settings.CACHE_PRE_KEY, REGISTRY_PRE_KEY, 'reg_apps']
    key = '.'.join(keys)

    value = apps.all_apps

    cache.set(key, value)

def get_reg_apps():
    """Gets all the registered apps from the cache
    """
    keys = [settings.CACHE_PRE_KEY, REGISTRY_PRE_KEY, 'reg_apps']
    key = '.'.join(keys)

    all_apps = cache.get(key)

    return all_apps
