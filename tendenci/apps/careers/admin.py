from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.careers.models import Career
from tendenci.apps.careers.forms import CareerForm
from tendenci.apps.site_settings.utils import get_setting


class CareerAdmin(TendenciBaseModelAdmin):
    list_display = ['user',
                    'company',
                    'position_title_str',
                    'position_type_str',
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
                        'sec',
                        'level',
                        'annual_salary',
                        'salary_increase',
                        'position_title',
                        'position_description',
                        'position_type',
                        'start_dt',
                        'end_dt',
                        'experience',
                )
        }),
        (_('Permissions'), {'fields': ('allow_anonymous_view',)}),
        (_('Advanced Permissions'), {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
            )}),
        (_('Status'), {'fields': (
            'status_detail',
            )}),
        )
    form = CareerForm
    ordering = ['-update_dt']

    class Media:
        pass

    def position_title_str(self, instance):
        return instance.position_title
    position_title_str.short_description = get_setting('module', 'careers', 'positiontitlelabel') or _('Position Title')
    position_title_str.admin_order_field = 'position_title'
    
    def position_type_str(self, instance):
        return instance.position_type
    position_type_str.short_description = get_setting('module', 'careers', 'positiontypelabel') or _('Position Type')
    position_type_str.admin_order_field = 'position_type'

admin.site.register(Career, CareerAdmin)
