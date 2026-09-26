from django.contrib.auth.models import User
from rest_framework import serializers

from tendenci.apps.profiles.models import Profile
from tendenci.apps.memberships.models import MembershipDemographic
from ..groups.serializers import GroupSerializer
# HyperlinkedModelSerializer


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["company", 'member_number', 'phone', 'address']

 
class MembershipDemographicSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipDemographic
        fields = ["ud1", 'ud2', 'ud3', 'ud4', 'ud5', 'ud6', 'ud7', 'ud8', 'ud9', 'ud10',
                  "ud11", 'ud12', 'ud13', 'ud14', 'ud15', 'ud16', 'ud17', 'ud18', 'ud19', 'ud20',
                  "ud21", 'ud22', 'ud23', 'ud24', 'ud25', 'ud26', 'ud27', 'ud28', 'ud29', 'ud30',]


class UserSerializer(serializers.ModelSerializer):
    user_groups = GroupSerializer(many=True, read_only=True)
    profile = ProfileSerializer(read_only=True)
    demographics = MembershipDemographicSerializer(read_only=True)
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", "email",
                  'profile', 'is_active', "date_joined",
                   "user_groups", "demographics"]