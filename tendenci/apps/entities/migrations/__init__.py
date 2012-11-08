from south.signals import post_migrate
from django.db import connection

from tendenci.core.site_settings.models import Setting
from tendenci.apps.entities.models import Entity
from tendenci.core.site_settings.utils import get_setting


def create_default_entity(sender, app, **kwargs):
    """
    Auto-create an entity with id=1 if none exist.
    """
    if app == "entities":
        if not Entity.objects.filter(pk=1):
            site_name = "Default"
            table_exists = Setting._meta.db_table in \
                connection.introspection.table_names()
            if table_exists and get_setting("site", "global", "sitedisplayname"):
                site_name = get_setting("site", "global", "sitedisplayname")

            entity = Entity()
            entity.allow_anonymous_view = False
            entity.entity_name = site_name
            entity.id = 1

            entity.save()

post_migrate.connect(create_default_entity)
