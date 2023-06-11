from django.db import models


class UnPushedItem(models.Model):
    """
    Serve as a queue to store the items to be pushed to Higher Logic.
    """
    user_id = models.PositiveIntegerField(null=True)
    event_id = models.PositiveIntegerField(null=True)
    # unique identifier: account_id for profiles, event-id for events
    identifier = models.CharField(max_length=10)
    deleted = models.BooleanField(default=False)
    create_dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'higher_logic'