from django.contrib import admin

from tendenci.core.perms.admin import TendenciBaseModelAdmin
from tendenci.addons.industries.models import Industry
from tendenci.addons.industries.forms import IndustryForm


class IndustryAdmin(TendenciBaseModelAdmin):
    list_display = ['industry_name', 'industry_code',
                    'owner_link', 'admin_perms',
                    'admin_status']
    list_filter = ['status_detail', 'owner_username']
    search_fields = ['industry_name', 'industry_code']
    fieldsets = (
        ('Industry Information', {
            'fields': ('industry_name',
                       'industry_code',
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
            'status_detail',
            )}),
        )
    form = IndustryForm
    ordering = ['-update_dt']

admin.site.register(Industry, IndustryAdmin)
