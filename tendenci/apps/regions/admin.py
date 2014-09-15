from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.regions.models import Region
from tendenci.apps.regions.forms import RegionForm


class RegionAdmin(TendenciBaseModelAdmin):
    list_display = ['region_name', 'region_code',
                    'owner_link', 'admin_perms',
                    'admin_status']
    list_filter = ['status_detail', 'owner_username']
    search_fields = ['region_name', 'region_code']
    fieldsets = (
        (_('Region Information'), {
            'fields': ('region_name',
                       'region_code',
                       'description',
                )
        }),
        (_('Permissions'), {'fields': ('allow_anonymous_view',)}),
        (_('Advanced Permissions'), {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
            )}),
        ('Status', {'fields': (
            'status_detail',
            )}),
        )
    form = RegionForm
    ordering = ['-update_dt']

admin.site.register(Region, RegionAdmin)
