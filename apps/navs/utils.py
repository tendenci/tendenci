from django.core.cache import cache
from django.template.loader import render_to_string
from django.forms.models import model_to_dict
from navs.cache import NAV_PRE_KEY
from navs.models import Nav

def cache_nav(nav):
    """
    Caches a nav's rendered html code
    """
    
    keys = [NAV_PRE_KEY, str(nav.id)]
    key = '.'.join(keys)
    value = render_to_string("navs/render_nav.html", {'nav':nav})
    is_set = cache.add(key, value, 432000) #5 days
    if not is_set:
        cache.set(key, value, 432000) #5 days
        
def get_nav(id):
    """
    Get the nav from the cache.
    """
    keys = [NAV_PRE_KEY, str(id)]
    key = '.'.join(keys)
    nav = cache.get(key)
    return nav
