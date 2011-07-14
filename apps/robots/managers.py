from django.db.models import Manager
from django.core.cache import cache

from robots.cache import CACHE_PRE_KEY, cache_all_robots

class RobotManager(Manager):
    def get_by_agent(self, user_agent):
        robots = cache.get(CACHE_PRE_KEY + '.all')
        if not robots:
            cache_all_robots()
            robots = cache.get(CACHE_PRE_KEY + '.all', [])
        
        for robot in robots:
            if robot.name.lower() in user_agent.lower():
                return robot
        return None
