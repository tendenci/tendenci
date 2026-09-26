from rest_framework import permissions, viewsets
from rest_framework_api_key.permissions import HasAPIKey
from django_filters import rest_framework as filters

from tendenci.apps.memberships.models import MembershipDefault, MembershipType

from .serializers import MembershipSerializer, MembershipTypeSerializer


class MembershipFilter(filters.FilterSet):
    start_date = filters.IsoDateTimeFilter(field_name="create_dt", lookup_expr='gte')
    end_date = filters.IsoDateTimeFilter(field_name="create_dt", lookup_expr='lte')
    approved_date_start = filters.IsoDateTimeFilter(field_name="application_approved_dt", lookup_expr='gte')
    approved_date_end = filters.IsoDateTimeFilter(field_name="application_approved_dt", lookup_expr='lte')

    class Meta:
        model = MembershipDefault
        fields = ['member_number', "user_id", 'start_date', 'end_date',
                  'approved_date_start', 'approved_date_end']


class MembershipViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows memberships to be viewed.
    """

    queryset = MembershipDefault.objects.filter(status=True,
                                             status_detail='active'
                                             ).order_by("-create_dt")
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAdminUser | HasAPIKey]
    filterset_class = MembershipFilter


class MembershipTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows membership types to be viewed.
    """

    queryset = MembershipType.objects.filter(status=True,
                                             status_detail='active'
                                             ).order_by("position")
    serializer_class = MembershipTypeSerializer
    permission_classes = [permissions.IsAdminUser | HasAPIKey]


