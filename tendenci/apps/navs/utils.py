from django.core.cache import cache
from django.conf import settings
from django.template.loader import render_to_string

from tendenci.apps.navs.cache import NAV_PRE_KEY


def get_pre_key(is_site_map=False):
    if is_site_map:
        return 'site_map'
    return NAV_PRE_KEY

def cache_nav(nav, show_title=False, is_site_map=False):
    """
    Caches a nav's rendered html code
    """
    keys = [settings.CACHE_PRE_KEY, get_pre_key(is_site_map), str(nav.id)]
    key = '.'.join(keys)
    value = render_to_string(template_name="navs/render_nav.html",
                        context={'nav':nav,
                         "show_title": show_title,
                         'is_site_map': is_site_map})
    cache.set(key, value, 432000) #5 days
    return value

def get_nav(id, is_site_map=False):
    """
    Get the nav from the cache.
    """
    keys = [settings.CACHE_PRE_KEY, get_pre_key(is_site_map), str(id)]
    key = '.'.join(keys)
    nav = cache.get(key)
    return nav

def clear_nav_cache(nav):
    """
    Clear nav cache
    """
    # delete nav and sitemap cache
    for is_site_map in [False, True]:
        keys = [settings.CACHE_PRE_KEY, get_pre_key(is_site_map), str(nav.id)]
        key = '.'.join(keys)
        cache.delete(key)
