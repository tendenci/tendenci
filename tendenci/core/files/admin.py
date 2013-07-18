from django.contrib import admin
from django.core.urlresolvers import reverse

from tendenci.core.perms.admin import TendenciBaseModelAdmin
from tendenci.core.files.models import File
from tendenci.core.files.forms import FileForm


class FileAdmin(TendenciBaseModelAdmin):
    list_display = ['file_preview', 'name', 'file_path', 'owner_link', 'admin_perms', 'admin_status']
    list_filter = ['status', 'owner_username']
    prepopulated_fields = {}
    search_fields = ['file', 'tags']
    fieldsets = (
        ('File Information', {
            'fields': ('file',
                       'name',
                       'tags',
                       'group',
                       )
        }),
        ('Permissions', {'fields': ('allow_anonymous_view',)}),
        ('Advanced Permissions', {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
    )
    form = FileForm
    ordering = ['-update_dt']

    def file_preview(self, obj):
        if obj.type() == "image":
            if obj.file:
                args = [obj.pk]
                args.append("100x50")
                args.append("crop")
                return '<img alt="%s" src="%s" />' % (obj, reverse('file', args=args))
            else:
                return ""
        elif obj.icon():
            return '<img alt="%s" src="%s" />' % (obj.type(), obj.icon())
        else:
            return obj.type()
    file_preview.allow_tags = True
    file_preview.short_description = 'Preview'

    def file_path(self, obj):
        return obj.file
    file_path.short_description = "File Path"

admin.site.register(File, FileAdmin)
