from django.contrib import admin

from tendenci.core.perms.admin import TendenciBaseModelAdmin
from tendenci.addons.careers.models import Career
from tendenci.addons.careers.forms import CareerForm


class CareerAdmin(TendenciBaseModelAdmin):
    list_display = ['user',
                    'company',
                    'position_title',
                    'position_type',
                    'start_dt',
                    'end_dt',
                    'admin_perms',
                    'admin_status']
    list_filter = ['status_detail', 'user']
    search_fields = ['user', 'company']
    fieldsets = (
        ('', {
            'fields': ('user',
                        'company',
                        'company_description',
                        'position_title',
                        'position_description',
                        'position_type',
                        'start_dt',
                        'end_dt',
                        'experience',
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
    form = CareerForm
    ordering = ['-update_dt']

admin.site.register(Career, CareerAdmin)
