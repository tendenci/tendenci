from django.core.cache import cache
from django.conf import settings

from tendenci.apps.navs.cache import NAV_PRE_KEY


def update_nav_links(sender, instance, **kwargs):
    keys = [settings.CACHE_PRE_KEY, NAV_PRE_KEY, str(instance.id)]
    key = '.'.join(keys)

    cache.delete(key)
