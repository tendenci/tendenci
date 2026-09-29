from rest_framework import permissions, viewsets
from rest_framework_api_key.permissions import HasAPIKey

from tendenci.apps.entities.models import Entity
from .serializers import EntitySerializer


class EntityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Returns a list of all entities.
    """

    queryset = Entity.objects.filter(status=True,
                                     status_detail='active').order_by("entity_name")
    serializer_class = EntitySerializer
    permission_classes = [permissions.IsAdminUser | HasAPIKey]
