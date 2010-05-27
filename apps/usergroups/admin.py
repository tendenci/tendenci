from django.contrib import admin

# Add your admin site registrations here, eg.
from usergroups.models import Group, GroupMembership
admin.site.register(Group)
admin.site.register(GroupMembership)