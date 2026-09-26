from rest_framework import permissions, viewsets
from rest_framework_api_key.permissions import HasAPIKey
from tendenci.apps.user_groups.models import Group

from .serializers import GroupSerializer


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser | HasAPIKey]