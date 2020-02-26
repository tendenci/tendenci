from django.db.models.signals import post_save
from django.contrib.auth.models import User


def create_usersettings(sender, instance, created, **kwargs):
    """
    Helper function to create UserSettings instances as
    required, eg when we first create the UserSettings database
    table via 'migrate' or when we save a new user.

    If we end up with users with no UserSettings, then we get horrible
    'DoesNotExist: UserSettings matching query does not exist.' errors.
    """
    from tendenci.apps.helpdesk.settings import DEFAULT_USER_SETTINGS
    from tendenci.apps.helpdesk.models import UserSettings
    if created:
        UserSettings.objects.create(user=instance, settings=DEFAULT_USER_SETTINGS)

def init_signals():
    post_save.connect(create_usersettings, sender=User, weak=False)
