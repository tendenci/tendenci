from south.signals import post_migrate
from django.db import connection
from django.core.management import call_command

from tendenci.core.site_settings.models import Setting
from tendenci.apps.entities.models import Entity
from tendenci.core.site_settings.utils import get_setting


def create_default_entity(sender, app, **kwargs):
    """
    Load default entities if none exist
    or create an entity with id=1 if not exist.
    """
    def get_site_display_name():
        setting_table_exists = Setting._meta.db_table in \
                    connection.introspection.table_names()
        if setting_table_exists:
            return get_setting("site", "global", "sitedisplayname")
        return ''

    if app == "entities":
        site_name = get_site_display_name().strip()
        if not Entity.objects.all():
            call_command("loaddata", "default_entities.json")
            if site_name:
                # update the entity_name of the first default entity
                entity = Entity.objects.get(pk=1)
                entity.entity_name = site_name
                entity.save()
        else:
            if not Entity.objects.filter(pk=1):
                if not site_name:
                    site_name = "Default"

                entity = Entity()
                entity.allow_anonymous_view = False
                entity.entity_name = site_name
                entity.id = 1

                entity.save()

# post_migrate.connect(create_default_entity)
