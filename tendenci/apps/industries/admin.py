from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.industries.models import Industry
from tendenci.apps.industries.forms import IndustryForm


class IndustryAdmin(TendenciBaseModelAdmin):
    list_display = ['industry_name', 'industry_code',
                    'owner_link', 'admin_perms',
                    'admin_status', 'position']
    list_filter = ['status_detail', 'owner_username']
    search_fields = ['industry_name', 'industry_code']
    list_editable = ['position']
    fieldsets = (
        (_('Industry Information'), {
            'fields': ('industry_name',
                       'industry_code',
                       'description',
                )
        }),
        (_('Permissions'), {'fields': ('allow_anonymous_view',)}),
        ('Advanced Permissions', {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
            )}),
        (_('Status'), {'fields': (
            'status_detail',
            )}),
        )
    form = IndustryForm
    ordering = ['position']

    class Media:
        css = {
            "all": ("css/websymbols.css",)
        }
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.11.0/jquery-ui.min.js',
            'js/admin/admin-list-reorder.js',
            'js/global/tinymce.event_handlers.js',
        )

admin.site.register(Industry, IndustryAdmin)
