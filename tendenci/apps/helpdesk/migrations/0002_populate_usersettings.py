
from django.contrib.auth import get_user_model
from django.db import migrations

from tendenci.apps.helpdesk.settings import DEFAULT_USER_SETTINGS


def pickle_settings(data):
    """Pickling as defined at migration's creation time"""
    import pickle
    from base64 import b64encode
    return b64encode(pickle.dumps(data)).decode()


# https://docs.djangoproject.com/en/1.7/topics/migrations/#data-migrations
def populate_usersettings(apps, schema_editor):
    """Create a UserSettings entry for each existing user.
    This will only happen once (at install time, or at upgrade)
    when the UserSettings model doesn't already exist."""

    _User = get_user_model()
    User = apps.get_model(_User._meta.app_label, _User._meta.model_name)

    # Import historical version of models
    UserSettings = apps.get_model("helpdesk", "UserSettings")

    settings_pickled = pickle_settings(DEFAULT_USER_SETTINGS)

    for u in User.objects.all():
        try:
            UserSettings.objects.get(user=u)
        except UserSettings.DoesNotExist:
            UserSettings.objects.create(user=u, settings_pickled=settings_pickled)


def noop(*args, **kwargs):
    return None

class Migration(migrations.Migration):

    dependencies = [
        ('helpdesk', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_usersettings, reverse_code=noop),
    ]
