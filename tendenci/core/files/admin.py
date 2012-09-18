from django.contrib import admin

from tendenci.core.perms.admin import TendenciBaseModelAdmin
from tendenci.core.files.models import File
from tendenci.core.files.forms import FileForm

class FileAdmin(TendenciBaseModelAdmin):
    list_display = ['file', 'name', 'owner_link', 'admin_perms', 'admin_status']
    list_filter = ['status', 'owner_username']
    prepopulated_fields = { }
    search_fields = ['file', 'tags']
    fieldsets = (
        ('File Information', {
            'fields': ('file',
                       'name',
                       'tags',
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
            )}),
        )
    form = FileForm
    ordering = ['-update_dt']

admin.site.register(File, FileAdmin)