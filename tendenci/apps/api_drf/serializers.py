# from django.contrib.auth.models import User
# from rest_framework import serializers
# from tendenci.apps.user_groups.models import Group
# from tendenci.apps.profiles.models import Profile
# # HyperlinkedModelSerializer
#
# class GroupSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Group
#         fields = ["id", "name"]
#
#
# class ProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Profile
#         fields = ["company", 'member_number', 'phone', 'address']
#
#
# class UserSerializer(serializers.ModelSerializer):
#     user_groups = GroupSerializer(many=True, read_only=True)
#     profile = ProfileSerializer(read_only=True)
#     class Meta:
#         model = User
#         fields = ["id", "username", "email", 'profile', "user_groups"]


