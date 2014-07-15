from django.db.models import Manager
from django.core.cache import cache
from django.conf import settings

from tendenci.core.robots.cache import CACHE_PRE_KEY, cache_all_robots


class RobotManager(Manager):
    def get_by_agent(self, user_agent):

        keys = [settings.CACHE_PRE_KEY, CACHE_PRE_KEY, 'all']
        key = '.'.join(keys)

        robots = cache.get(key)
        if not robots:
            cache_all_robots()
            robots = cache.get(key, [])

        # UnicodeDecodeError: 'ascii' codec can't decode byte 0xf3
        # http://stackoverflow.com/questions/2392732/sqlite-python-unicode-and-non-utf-data
        user_agent = unicode(user_agent, errors='ignore')

        for robot in robots:
            if robot.name.lower() in user_agent.lower():
                return robot
        return None
