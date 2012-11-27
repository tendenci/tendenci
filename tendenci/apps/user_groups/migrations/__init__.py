from south.signals import post_migrate
from django.db import connection

from tendenci.core.site_settings.models import Setting
from tendenci.apps.user_groups.models import Group
from tendenci.core.site_settings.utils import get_setting


def create_default_group(sender, app, **kwargs):
    """
    Auto-create a default group with id=1 if none exist.
    """
    if app == "user_groups":
        if not Group.objects.filter(pk=1):
            site_name = "Default"
            table_exists = Setting._meta.db_table in \
                connection.introspection.table_names()
            if table_exists and get_setting("site", "global", "sitedisplayname"):
                site_name = get_setting("site", "global", "sitedisplayname")

            group = Group()
            group.name = site_name
            group.label = site_name
            group.show_as_option = False
            group.allow_self_add = False
            group.allow_self_remove = False
            group.description = "Initial group auto-generated on site creation."
            group.id = 1

            group.save()

post_migrate.connect(create_default_group)
