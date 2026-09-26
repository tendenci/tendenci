from rest_framework import permissions, viewsets
from rest_framework_api_key.permissions import HasAPIKey

from tendenci.apps.events.models import Event
from .serializers import EventSerializer


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows entities to be viewed.
    """

    queryset = Event.objects.filter(status=True,
                                    status_detail='active'
                                    ).order_by("-start_dt")
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAdminUser | HasAPIKey]