from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.user_groups.models import Group, GroupMembership
from tendenci.apps.user_groups.forms import GroupAdminForm
from tendenci.apps.perms.admin import TendenciBaseModelAdmin


class GroupAdmin(TendenciBaseModelAdmin):
    list_display = ['id', 'name', 'label', 'entity', 'dashboard_url', 'show_as_option', 'allow_self_add', 'allow_self_remove', 'admin_status']
    search_fields = ['name', 'label', 'entity__entity_name']
    list_filter = ['entity', 'show_as_option', 'allow_self_add']
    list_editable = ['name', 'label', 'entity']
    fieldsets = (
        (None, {'fields': ('name', 'label', 'entity', 'email_recipient', 'permissions')}),
        (_('Flags'), {'fields': (
            'show_as_option', 'allow_self_add', 'allow_self_remove', 'sync_newsletters')}),
        (_('Administrative'), {'fields': (
            'allow_anonymous_view', 'user_perms', 'member_perms', 'group_perms', 'status_detail')}),
    )
    form = GroupAdminForm

#     def has_delete_permission(self, request, obj=None):
#         if obj and obj.type == 'system_generated':
#             return False
#         return super(GroupAdmin, self).has_delete_permission(request, obj=obj)


class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ['group', 'member']
    search_fields = ['group', 'member']
    fieldsets = (
        (None, {'fields': ('group', 'member')}),
    )

admin.site.register(Group, GroupAdmin)
#admin.site.register(GroupMembership, GroupMembershipAdmin)

from django.contrib.auth.models import Group as AuthGroup
# unregister AuthGroup
admin.site.unregister(AuthGroup)
