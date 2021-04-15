from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.regions.models import Region
from tendenci.apps.regions.forms import RegionForm
from tendenci.apps.theme.templatetags.static import static


class RegionAdmin(TendenciBaseModelAdmin):
    list_display = ['region_name', 'region_code',
                    'owner_link', 'admin_perms',
                    'admin_status', 'position']
    list_filter = ['status_detail', 'owner_username']
    search_fields = ['region_name', 'region_code']
    list_editable = ['position']
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

    class Media:
        css = {
            "all": (static("css/websymbols.css"),)
        }
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js',
            static('js/admin/admin-list-reorder.js'),
            static('js/global/tinymce.event_handlers.js'),
        )

admin.site.register(Region, RegionAdmin)
