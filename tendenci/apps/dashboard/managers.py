from django.db import models


class DashboardStatManager(models.Manager):
    def get_latest(self, key):
        if self.get_query_set().filter(key=key).exists():
            return self.get_query_set().filter(key=key)[0]
        return None
