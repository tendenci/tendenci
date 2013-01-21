from south.signals import post_migrate
from django.db import connection
from django.core.management import call_command

from tendenci.core.site_settings.models import Setting
from tendenci.apps.user_groups.models import Group
from tendenci.core.site_settings.utils import get_setting


def create_default_group(sender, app, **kwargs):
    """
    Load default groups if none exist
    or create a group with id=1 if not exist.
    """
    def get_site_display_name():
        setting_table_exists = Setting._meta.db_table in \
                    connection.introspection.table_names()
        if setting_table_exists:
            return get_setting("site", "global", "sitedisplayname")
        return ''

    if app == "user_groups":
        site_name = get_site_display_name().strip()
        if not Group.objects.all():
            call_command("loaddata", "default_groups.json")
            if site_name:
                # update the name and label of the first default user group
                group = Group.objects.get(pk=1)
                group.name = site_name
                group.label = site_name
                group.save()
        else:
            if not Group.objects.filter(pk=1):
                if not site_name:
                    site_name = "Default"

                group = Group()
                group.name = site_name
                group.label = site_name
                group.show_as_option = False
                group.allow_self_add = False
                group.allow_self_remove = False
                group.description = "Initial group auto-generated on site creation."
                group.id = 1

                group.save()

# post_migrate.connect(create_default_group)
