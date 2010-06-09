from django.core.cache import cache

from robots.models import Robot

SETTING_PRE_KEY = "robots"

def cache_all_robots():
    """ Caches all query of robots """
    key = [SETTING_PRE_KEY, 'all']
    key = '.'.join(key)
    
    robots = Robot.objects.all()
    is_set = cache.add(key, robots)
    if not is_set:
        cache.set(key, robots)