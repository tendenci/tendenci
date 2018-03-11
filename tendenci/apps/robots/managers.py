from builtins import str

from django.db.models import Manager
from django.core.cache import cache
from django.conf import settings
from django.db.models.query import QuerySet

from tendenci.apps.robots.cache import CACHE_PRE_KEY, cache_all_robots


class RobotManager(Manager):
    def get_by_agent(self, user_agent):

        keys = [settings.CACHE_PRE_KEY, CACHE_PRE_KEY, 'all']
        key = '.'.join(keys)

        robots = cache.get(key)
        if not (robots and isinstance(robots, QuerySet)):
            cache_all_robots()
            robots = cache.get(key, [])

        # UnicodeDecodeError: 'ascii' codec can't decode byte 0xf3
        # http://stackoverflow.com/questions/2392732/sqlite-python-unicode-and-non-utf-data
        try:
            user_agent = str(user_agent, errors='ignore')
        except TypeError:
            pass

        for robot in robots:
            if robot.name.lower() in user_agent.lower():
                return robot
        return None
