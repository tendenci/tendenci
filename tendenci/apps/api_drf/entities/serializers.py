from rest_framework import serializers

from tendenci.apps.entities.models import Entity


class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ["id", "entity_name", "entity_type", "entity_parent_id",
                  "status_detail"]