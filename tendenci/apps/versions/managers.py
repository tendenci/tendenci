import uuid

from django.db.models import Manager
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
import simplejson as json


class VersionManager(Manager):
    def save_version(self, old_instance, new_instance, **kwargs):
        if old_instance and new_instance:
            version = self.model()
            changes = []
            for field in old_instance._meta.fields:
                field = unicode(field.name)
                if "create_dt" in field or "update_dt" in field:
                    continue

                if hasattr(old_instance, field):
                    old = getattr(old_instance, field)
                    new = getattr(new_instance, field)
                    if old != new:
                        if old and hasattr(old, '_meta'):
                            old = serializers.serialize('json', [old], ensure_ascii=False)
                        if new and hasattr(new, '_meta'):
                            new = serializers.serialize('json', [new], ensure_ascii=False)
                        changes.append({
                            "field": field,
                            "old": old,
                            "new": new,
                        })

            if changes:
                version.content_type = ContentType.objects.get_for_model(old_instance)
                version.object_id = old_instance.pk
                version.object_repr = unicode(old_instance)[:50]
                version.user = old_instance.owner
                version.create_dt = old_instance.update_dt
                version.hash = str(uuid.uuid1())

                version.object_changes = json.dumps(changes, cls=DjangoJSONEncoder)

                object_json = serializers.serialize('json', [old_instance], ensure_ascii=False)
                object_value = object_json[1:-1]
                version.object_value = object_value
                version.save()

                return version
        return None
