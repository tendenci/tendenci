from south.signals import post_migrate
from south.models import MigrationHistory

from tendenci.apps.user_groups.models import Group
from tendenci.core.site_settings.utils import get_setting


def create_default_group(sender, app, **kwargs):
    """
    Auto-create a default group if no groups exist.
    """
    if MigrationHistory.objects.filter(app_name="site_settings").count() > 0 and app == "user_groups" and not Group.objects.all().exists():
        site_name = get_setting("site", "global", "sitedisplayname")
        group = Group()
        if site_name:
            group.name = site_name
        else:
            group.name = "Default"
        group.show_as_option = False
        group.allow_self_add = False
        group.allow_self_remove = False
        group.description = "Initial group auto-generated on site creation."

        group.save()

post_migrate.connect(create_default_group)
