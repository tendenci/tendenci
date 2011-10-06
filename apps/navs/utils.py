from django.core.cache import cache
from django.template.loader import render_to_string
from django.forms.models import model_to_dict
from navs.cache import NAV_PRE_KEY
from navs.models import Nav

def cache_nav(nav):
    """
    Caches a nav and all its items
    The cache should be a nested dictionary so we can 
    smoothly load the subnavs under their parents
    """
    
    keys = [NAV_PRE_KEY, unicode(nav.id)]
    key = '.'.join(keys)
    value = render_to_string("navs/render_nav.html", {'nav':nav})
    is_set = cache.add(key, value)
    if not is_set:
        cache.set(key, value)
        
def get_nav(id):
    """
    Get the nav from the cache.
    Get it from the db if its not in the cache.
    """
    keys = [NAV_PRE_KEY, unicode(id)]
    key = '.'.join(keys)
    nav = cache.get(key)
    return nav

def nav_to_dict(nav):
    """
        Create a dictionary version of a Nav and
        include the items into it.
    """
    d = model_to_dict(nav)
    for item in nav.items:
        d['items'] = item_to_dict(item)
    return d
    
def item_to_dict(item):
    d = model_to_dict(item)
    for child in d.children:
        d['children'] = item_to_dict(child)
    return d
