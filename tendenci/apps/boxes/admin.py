from django.contrib import admin
from django.conf import settings

from tendenci.core.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.boxes.models import Box
from tendenci.apps.boxes.forms import BoxForm


class BoxAdmin(TendenciBaseModelAdmin):
    list_display = ('edit_link', 'pk', 'title', 'tags', 'content', 'admin_perms', 'admin_status')
    search_fields = ('title', 'content', 'tags',)
    fieldsets = (
        (None, {'fields': ('title', 'content', 'tags')}),
        ('Permissions', {'fields': ('allow_anonymous_view',)}),
        ('Advanced Permissions', {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        ('Publishing Status', {'fields': (
            'status',
            'status_detail'
        )}),
    )
    form = BoxForm

    class Media:
        js = (
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
        )

    def admin_status(self, obj):
        return obj.obj_status
    admin_status.allow_tags = True
    admin_status.short_description = 'status'

    def admin_perms(self, obj):
        return obj.obj_perms
    admin_perms.allow_tags = True
    admin_perms.short_description = 'permission'

admin.site.register(Box, BoxAdmin)
