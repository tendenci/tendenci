from rest_framework import serializers
from tendenci.apps.user_groups.models import Group
# HyperlinkedModelSerializer

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name"]