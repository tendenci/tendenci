from django.db import models
from django.contrib.auth.models import User


class UnPushedItem(models.Model):
    """
    Serve as a queue to store the items to be pushed to Authentik.
    """
    user_id = models.PositiveIntegerField()
    deleted = models.BooleanField(default=False)
    create_dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'authentik'


class AuthentikUserMapping(models.Model):
    user_id = models.PositiveIntegerField(unique=True)
    # authentik user id
    a_user_id = models.PositiveIntegerField()

    class Meta:
        app_label = 'authentik'