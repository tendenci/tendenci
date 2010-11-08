from django.contrib import admin
from memberships.models import MembershipType

class MembershipTypeAdmin(admin.ModelAdmin):
    pass

admin.site.register(MembershipType, MembershipTypeAdmin)