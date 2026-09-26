from django.contrib.auth.models import User
from rest_framework import permissions, viewsets
from rest_framework_api_key.permissions import HasAPIKey
from django_filters import rest_framework as filters

from .serializers import UserSerializer


class UserFilter(filters.FilterSet):
    start_date = filters.IsoDateTimeFilter(field_name="date_joined", lookup_expr='gte')
    end_date = filters.IsoDateTimeFilter(field_name="date_joined", lookup_expr='lte')

    class Meta:
        model = User
        fields = ['email', "is_active", 'start_date', 'end_date']


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser | HasAPIKey]
    filterset_class = UserFilter