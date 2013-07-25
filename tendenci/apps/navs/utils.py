from django.core.cache import cache
from django.conf import settings
from django.template.loader import render_to_string
from django.forms.models import model_to_dict
from tendenci.apps.navs.cache import NAV_PRE_KEY
from tendenci.apps.navs.models import Nav

def cache_nav(nav, show_title=False):
    """
    Caches a nav's rendered html code
    """
    
    keys = [settings.CACHE_PRE_KEY, NAV_PRE_KEY, str(nav.id)]
    key = '.'.join(keys)
    value = render_to_string("navs/render_nav.html", {'nav':nav, "show_title": show_title})
    is_set = cache.add(key, value, 432000) #5 days
    if not is_set:
        cache.set(key, value, 432000) #5 days
        
def get_nav(id):
    """
    Get the nav from the cache.
    """
    keys = [settings.CACHE_PRE_KEY, NAV_PRE_KEY, str(id)]
    key = '.'.join(keys)
    nav = cache.get(key)
    return nav
