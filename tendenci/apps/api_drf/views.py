# from django.contrib.auth.models import User
# from rest_framework import permissions, viewsets
# from rest_framework_api_key.permissions import HasAPIKey
# from tendenci.apps.user_groups.models import Group
#
# from .serializers import GroupSerializer, UserSerializer
#
#
# class UserViewSet(viewsets.ReadOnlyModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#
#     queryset = User.objects.all().order_by("-date_joined")
#     serializer_class = UserSerializer
#     permission_classes = [permissions.IsAdminUser | HasAPIKey]
#
#
# class GroupViewSet(viewsets.ReadOnlyModelViewSet):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#
#     queryset = Group.objects.all().order_by("name")
#     serializer_class = GroupSerializer
#     permission_classes = [permissions.IsAdminUser | HasAPIKey]