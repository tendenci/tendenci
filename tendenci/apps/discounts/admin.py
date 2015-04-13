from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.discounts.models import Discount
from tendenci.apps.discounts.forms import DiscountForm


class DiscountAdmin(TendenciBaseModelAdmin):
    list_display = ['discount_code', 'start_dt', 'end_dt', 'value', 'admin_perms', 'admin_status']
    list_filter = ['status_detail', 'owner_username']
    prepopulated_fields = {}
    search_fields = ['discount_code', 'start_dt', 'end_dt', 'value']
    fieldsets = (
        (_('Discount Information'), {
            'fields': (
                'discount_code',
                'start_dt',
                'end_dt',
                'value',
                'cap',
            )
        }),
        (_('Permissions'), {
            'fields': ('allow_anonymous_view',)
        }),
        ('Advanced Permissions', {
            'classes': ('collapse',),
            'fields': (
                'user_perms',
                'member_perms',
                'group_perms',
            )
        }),
        (_('Status'), {
            'fields': (
                'status_detail',
            )
        }),
    )
    form = DiscountForm
    ordering = ['-update_dt']

admin.site.register(Discount, DiscountAdmin)
