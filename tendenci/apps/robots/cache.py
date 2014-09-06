from django.core.cache import cache
from django.conf import settings


CACHE_PRE_KEY = "robots"

def cache_all_robots():
    """ Caches all query of robots """
    from tendenci.apps.robots.models import Robot

    keys = [settings.CACHE_PRE_KEY, CACHE_PRE_KEY, 'all']
    key = '.'.join(keys)

    robots = Robot.objects.all()
    cache.set(key, robots)
