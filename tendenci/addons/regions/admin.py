from django.contrib import admin

from tendenci.core.perms.admin import TendenciBaseModelAdmin
from tendenci.addons.regions.models import Region
from tendenci.addons.regions.forms import RegionForm


class RegionAdmin(TendenciBaseModelAdmin):
    list_display = ['region_name', 'region_code',
                    'owner_link', 'admin_perms',
                    'admin_status']
    list_filter = ['status_detail', 'owner_username']
    search_fields = ['region_name', 'region_code']
    fieldsets = (
        ('Region Information', {
            'fields': ('region_name',
                       'region_code',
                       'description',
                )
        }),
        ('Permissions', {'fields': ('allow_anonymous_view',)}),
        ('Advanced Permissions', {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
            )}),
        ('Status', {'fields': (
            'status',
            'status_detail',
            )}),
        )
    form = RegionForm
    ordering = ['-update_dt']

admin.site.register(Region, RegionAdmin)
